"""Module for RPC (remote prodedure call, a.k.a. call-and-response) type RabbitMQ communication"""

# ----------------------------------------------------------------------------------
# Created on Thu Feb 27 2025
#
# Copyright (c) 2025 Colorado State University. All rights reserved. (1)
#
# Contributors:
#     Mackenzie Grimes (1)
#
# ----------------------------------------------------------------------------------
import logging
import logging.config
import uuid
from collections.abc import Callable
from concurrent.futures import Future
from copy import deepcopy
from typing import NamedTuple

from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from .rabbitmq_utils import (
    Conn,
    Consumer,
    Exch,
    Queue,
    RabbitMqParams,
    RabbitMqParamsAndCallback,
    RabbitMqMessage,
    DIRECT_REPLY_QUEUE,
    threadsafe_ack,
    threadsafe_nack,
    blocking_publish,
)

logger = logging.getLogger(__name__)


class RpcResponse(NamedTuple):
    """Data class to specify how result of RPC request should be communicated to the RMQ broker.
    Either ack or nack with no requeue (usually a response RabbitMqMessage should be published),
    or nack with requeue True (to re-attempt processing).

    Message can be None (and is None by default), meaning request is only acked/nacked without
    a response to the awaiting requestor, but this should generally only be used if requeue=True.
    """

    message: RabbitMqMessage | None
    ack: bool = True
    requeue: bool = False


class RpcPublisher:
    """RabbitMQ RPC (remote procedure call) publishing client, runs in own thread to not block
    heartbeat. This class can be used to send "requests" (outbound messages) over RabbitMQ and
    block until a "response" (inbound message) comes back from an `RpcConsumer` instance.
    All producing to/consuming of different queues and associating requests with their responses
    is abstracted away.

    By RabbitMQ convention, RPC uses the built-in Direct Reply-To queue to field responses messages,
    which generates a temporary, random queue name for that individual message, rather than
    creating its own durable queue. Directing responses to a custom queue is not yet supported.

    The `start()` and `stop()` methods should be called from the same thread that created the
    `RpcPublisher` instance.

    Example usage:
        ```
        my_client = RpcPublisher(...insert RabbitMQ parameters...)
        my_client.start()

        response = my_client.send_message(RabbitMqMessage('{"some": "json"}'))
        # blocks while waiting for response
        logger.info(f'Got response from external service: {response}')
        ```
    """

    def __init__(self, conn_params: Conn, exch: Exch, timeout: float | None = None):
        """
        Args:
            conn_params (Conn): parameters to connect to RabbitMQ server
            exch (Exch): parameters of RMQ Exchange where messages should be sent
            timeout (float | None): optional timeout to give up on receiving each response.
                Default is None, meaning wait indefinitely for response from external RMQ service.
        """
        self._exch = exch
        self._timeout = timeout
        # only publish to built-in Direct Reply-to queue (recommended for RPC, less setup needed)
        self._queue = Queue(DIRECT_REPLY_QUEUE, "", True, False, False)

        # worklist to track corr_ids sent to remote service, and associated response when it arrives
        self._pending_requests: dict[str, Future] = {}

        # Start long-running thread to consume any messages from response queue
        self._consumer = Consumer(
            conn_params,
            RabbitMqParamsAndCallback(
                RabbitMqParams(Exch("", "direct"), self._queue), self._on_response
            ),
        )

    @property
    def is_open(self) -> bool:
        """Returns True if RabbitMQ connection (Publisher) is open and ready to send messages"""
        return self._consumer.is_alive() and self._consumer.channel.is_open

    def send_request(self, request: RabbitMqMessage) -> RabbitMqMessage | None:
        """Send message to remote RabbitMQ service using thread-safe RPC. Will block until response
        is received back, or timeout occurs.

        Args:
            request (RabbitMqMessage): the RabbitMQ message body and (optional) properties to send
                as a "request" to the listening RpcConsumer service.

        Returns:
            RabbitMqMessage | None: The response message (body and properties), or None on request
                timeout or error handling response.
        """
        if not self.is_open:
            logger.debug("RPC thread not yet initialized. Setting up now")
            self.start()

        # generate unique ID to associate our request to external service's response
        request_id = str(uuid.uuid4())

        # send request to external RMQ service, providing unique RPC message ID and
        # the queue where it should respond
        if request.properties.headers is None:
            request.properties.headers = {}
        request.properties.headers["rpc"] = request_id
        request.properties.reply_to = self._queue.name

        # overwrite routing key (if any) to enforce use of default Exchange and Direct Reply-to
        request = RabbitMqMessage(request.body, request.properties, self._exch.route_key)

        # add future to dict where callback can retrieve it and set result
        request_future = Future()
        self._pending_requests[request_id] = request_future

        logger.debug("Publishing request message to external service with body: %s", request.body)
        blocking_publish(self._consumer.channel, self._exch, request, self._queue)

        try:
            # block until callback runs (we'll know when the future's result has been changed)
            return request_future.result(timeout=self._timeout)
        except TimeoutError:
            logger.warning("Timed out waiting for response. rpc request_id: %s", request_id)
            self._pending_requests.pop(request_id)  # stop tracking request Future
            return None
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Unexpected response from external service: %s", str(exc))
            self._pending_requests.pop(request_id)  # stop tracking request Future
            return None

    def start(self):
        """Start dedicated threads to asynchronously send and receive RPC messages using a new
        RabbitMQ connection and channel. Note: this method can be called externally, but it is
        not required to use the client. It will automatically call this internally as needed."""
        if not self.is_open:
            logger.debug("Starting RPC thread to send and consume messages")
            self._consumer.start()

    def stop(self):
        """Unsubscribe to Direct Reply-To queue and cleanup thread"""
        logger.debug("Shutting down RPC threads")
        if not self.is_open:
            logger.debug("RPC threads not running, nothing to cleanup")
            return

        # tell Consumer cleanup RabbitMQ resources and wait for thread to terminate
        self._consumer.stop()
        self._consumer.join()

    def _on_response(
        self, channel: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes
    ):
        """Handle RabbitMQ message emitted to response queue."""
        logger.debug(
            "Received response with routing_key: %s, content_type: %s, message: %i",
            method.routing_key,
            properties.content_type,
            str(body, encoding="utf-8"),
        )

        # messages sent through RabbitMQ Direct reply-to are auto acked
        is_direct_reply = str(method.routing_key).startswith(DIRECT_REPLY_QUEUE)

        # remove future from pending list. we will update result shortly
        request_id = properties.headers.get("rpc")
        if request_id not in self._pending_requests:
            logger.debug(
                (
                    "Received response whose headers.rpc does not match any pending "
                    "request, may have already timed out. headers: %s"
                ),
                properties.headers,
            )
            if not is_direct_reply:
                channel.basic_ack(delivery_tag=method.delivery_tag)
            return None

        request_future = self._pending_requests.pop(request_id)
        if not is_direct_reply:
            channel.basic_ack(delivery_tag=method.delivery_tag)

        # update future with response body to communicate it back up to main thread
        return request_future.set_result(RabbitMqMessage(str(body, encoding="utf-8"), properties))


class RpcConsumer:
    """Consumer RPC (remote prodecure call) class that serves as the listener to `RpcPublisher`
    messages. `RpcConsumer` creates a thread to constantly consume RPC message "requests" emitted
    by `RpcPublisher`, form a response, and send back it to the `RpcPublisher` asynchronously.

    Note that RPC by RabbitMQ convention uses built-in Direct Reply-to queue over the default
    exchange, and listeners for responses on a temporary queue unique to a given RPC request.
    Publishing RpcConsumer responses to a custom, durable queue is not yet supported.

    Example usage:
        ```
        def on_receive_request(message: RabbitMqMessage):
            logger.info('Got request from external service: %s', message.body)
            if message.properties.content_type == 'application/json':
                return RpcResponse(RabbitMqMessage('success!'), ack=True)
            return RpcResponse(None, ack=False, requeue=True)

        my_consumer = RpcConsumer(<insert Conn>,
                                  RmqParams(<insert Exch>, <insert Queue>),
                                  on_receive_request)
        my_consumer.start()
        ```
    """

    def __init__(
        self,
        conn_params: Conn,
        rmq_params: RabbitMqParams,
        on_request_callback: Callable[[RabbitMqMessage], RpcResponse],
        *args,
        **kwargs,
    ):
        """
        Args:
            conn_params (Conn): parameters to connect to RabbitMQ server
            rmq_params (RabbitMqParams): parameters of RMQ Exchange and Queue where RPC messages
                are expected to be received from an `RpcPublisher`.
            on_message_callback (Callable[[RabbitMqMesssage], RpcResponse]): a function that
                receives an inbound RPC request message, does some work with it, then returns a
                RpcResponse, which controls if message should be acked/nacked and some
                RabbitMqMessage published back the original requester, or if the request
                should be nack'd and requeued to re-attempt processing
        """
        self._rmq_params = rmq_params
        self._on_request_callback = on_request_callback

        # Start long-running thread to consume any messages from response queue
        self._consumer = Consumer(
            conn_params, RabbitMqParamsAndCallback(rmq_params, self._on_message), *args, **kwargs
        )

    @property
    def is_open(self):
        """Returns True if RabbitMQ connection (Consumer) is open and ready to receive messages"""
        return self._consumer.is_alive() and self._consumer.channel.is_open

    def start(self):
        """Start dedicated threads to asynchronously receive, and send, RPC messages using a new
        RabbitMQ connection and channel. Note: this method can be called externally, but it is
        not required to use the client. It will automatically call this internally as needed."""
        if not self.is_open:
            logger.debug("Starting RPC thread to consume messages")
            self._consumer.start()
            self._consumer.join()

    def stop(self):
        """Unsubscribe to queue and cleanup thread(s)"""
        logger.debug("Shutting down RpcConsumer threads")
        if not self.is_open:
            logger.debug("RpcConsumer threads not running, nothing to cleanup")
            return

        # tell Consumer to cleanup RabbitMQ resources and wait for thread to terminate
        self._consumer.stop()
        self._consumer.join()

    def _on_message(
        self, channel: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes
    ):
        """Handle receiving a request message from an `RpcPublisher`. Invoke user-provided callback
        to form response body, then send RabbitMQ message over Exchange (likely default) and Queue
        (likely a unique Direct Reply-to) that `RpcPublisher` specified in message props.
        """
        request = body.decode()
        logger.debug("Received request message from external message with body: %s", request)
        response = self._on_request_callback(
            RabbitMqMessage(request, properties, method.routing_key)
        )

        if response.ack:
            threadsafe_ack(
                channel,
                method.delivery_tag,
                lambda: logger.debug("Request %s was acked", properties.headers.get("rpc")),
            )
        else:
            threadsafe_nack(
                channel,
                method.delivery_tag,
                lambda: logger.debug("Request %s was nacked", properties.headers.get("rpc")),
                requeue=response.requeue,
            )

        if content := response.message:
            # per RabbitMQ RPC convention, always use default Exchange so clients can operate on
            # any exchange and RabbitMQ will route the message to their queue correctly
            exch = Exch("", "direct", route_key=properties.reply_to)
            logger.info("Publishing response to default exchange, routing key: %s", exch.route_key)
            logger.debug("Publishing response to external request service: %s", content.body)

            # tag this response message using the "rpc" UUID from request's headers; required so
            # RpcPublisher can associate each request/response pair and resolve all pending Futures
            response_props = deepcopy(content.properties)
            response_props.reply_to = properties.reply_to
            if response_props.headers is None:
                response_props.headers = {}
            response_props.headers["rpc"] = properties.headers.get("rpc")

            blocking_publish(
                channel, exch, RabbitMqMessage(content.body, response_props, exch.route_key)
            )
