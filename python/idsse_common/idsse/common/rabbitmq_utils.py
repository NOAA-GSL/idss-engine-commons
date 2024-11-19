"""Module for RabbitMQ client related data classes and utility functions"""
# ----------------------------------------------------------------------------------
# Created on Fri Sep 8 2023.
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.  (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Paul Hamer (2)
#     Mackenzie Grimes (2)
#
# ----------------------------------------------------------------------------------

import contextvars
import logging
import logging.config
import uuid

from concurrent.futures import Future, ThreadPoolExecutor
from collections.abc import Callable
from functools import partial
from threading import Event, Thread
from typing import NamedTuple

from pika import BasicProperties, ConnectionParameters, PlainCredentials
from pika.adapters import BlockingConnection
from pika.channel import Channel
from pika.exceptions import UnroutableError
from pika.frame import Method
from pika.spec import Basic

logger = logging.getLogger(__name__)

# default pseudo-queue on default exchange that RabbitMQ designates for direct reply-to RPC
DIRECT_REPLY_QUEUE = 'amq.rabbitmq.reply-to'


class Conn(NamedTuple):
    """An internal data class for holding the RabbitMQ connection info"""
    host: str
    v_host: str
    port: int
    username: str
    password: str

    @property
    def connection_parameters(self) -> ConnectionParameters:
        """Convert Conn data object into pika.ConnectionParameters, ready to be passed
        to pika connection constructors such as BlockingConnection() or SelectConnection()"""
        return ConnectionParameters(
            host=self.host,
            virtual_host=self.v_host,
            port=self.port,
            credentials=PlainCredentials(self.username, self.password)
        )


class Exch(NamedTuple):
    """An internal data class for holding the RabbitMQ exchange info"""
    name: str
    type: str
    route_key: str = ''
    durable: bool = True
    delivery_conf: bool | None = False
    mandatory: bool | None = False


class Queue(NamedTuple):
    """An internal data class for holding the RabbitMQ queue info"""
    name: str
    route_key: str
    durable: bool
    exclusive: bool
    auto_delete: bool
    arguments: dict = {}


class RabbitMqParams(NamedTuple):
    """Data class to hold configurations for RabbitMQ exchange/queue pair"""
    exchange: Exch
    queue: Queue = None


class RabbitMqParamsAndCallback(NamedTuple):
    """
    Data class to hold configurations for RabbitMQ exchange/queue pair and the callback
    to be used when consuming from the queue
    """
    params: RabbitMqParams
    callback: Callable


def _initialize_exchange_and_queue(
    channel: Channel,
    params: RabbitMqParams
) -> str:
    """Declare and bind RabbitMQ exchange and queue using the provided channel.

    Returns:
        str: the name of the newly-initialized queue.
    """
    exch, queue = params
    logger.info('Subscribing to exchange: %s', exch.name)

    # Do not try to declare the default exchange. It already exists
    if exch.name != '':
        channel.exchange_declare(exchange=exch.name,
                                 exchange_type=exch.type,
                                 durable=exch.durable)

    # Do not try to declare or bind built-in queues. They are pseudo-queues that already exist
    if queue.name.startswith('amq.rabbitmq.'):
        return queue.name

    # If we have a 'private' queue, i.e. one used to support message publishing, not consumed
    # Set message time-to-live (TTL) to 10 seconds
    if queue.name.startswith('_'):
        queue.arguments['x-message-ttl'] = 10 * 1000
    frame: Method = channel.queue_declare(
        queue=queue.name,
        exclusive=queue.exclusive,
        durable=queue.durable,
        auto_delete=queue.auto_delete,
        arguments=queue.arguments
    )

    # Bind queue to exchange with routing_key. May need to support multiple keys in the future
    if exch.name != '':
        logger.info('    binding key %s to queue: %s', queue.route_key, queue.name)
        channel.queue_bind(queue.name, exch.name, queue.route_key)
    return frame.method.queue


def _initialize_connection_and_channel(
    connection: Conn,
    params: RabbitMqParams,
    channel: Channel | Channel | None = None,
) -> tuple[BlockingConnection, Channel, str]:
    """Establish RabbitMQ connection, and declare exchange and queue on new Channel"""
    if not isinstance(connection, Conn):
        # connection of unsupported type passed
        raise ValueError(
            (f'Cannot use or create new RabbitMQ connection using type {type(connection)}. '
             'Should be type Conn (a dict with connection parameters)')
        )

    _connection = BlockingConnection(connection.connection_parameters)
    logger.info('Established new RabbitMQ connection to %s on port %i',
                connection.host, connection.port)

    if channel is None:
        logger.info('Creating new RabbitMQ channel')
        _channel = _connection.channel()
    else:
        _channel = channel

    queue_name = _initialize_exchange_and_queue(_channel, params)

    return _connection, _channel, queue_name


def subscribe_to_queue(
    connection: Conn | BlockingConnection,
    rmq_params: RabbitMqParams,
    on_message_callback: Callable[
        [Channel, Basic.Deliver, BasicProperties, bytes], None],
    channel: Channel | None = None
) -> tuple[BlockingConnection, Channel]:
    """
    Function that handles setup of consumer of RabbitMQ queue messages, declaring the exchange and
    queue if needed, and invoking the provided callback when a message is received.

    If an existing BlockingConnection or BlockingChannel are passed, they are used to
    set up the subscription, but by default a new connection and channel will be established and
    returned, which the caller can immediately begin doing RabbitMQ operations with.

    For example: start a blocking consume of messages with channel.start_consuming(), or
    close gracefully with connection.close()

    Args:
        connection (Conn | BlockingConnection): connection parameters to establish new
            RabbitMQ connection, or existing RabbitMQ connection to reuse for this consumer.
        rmq_params (RabbitMqParams): parameters for the RabbitMQ exchange and queue from which to
            consume messages.
        on_message_callback (Callable[
            [BlockingChannel, Basic.Deliver, BasicProperties, bytes], None]):
            function to handle messages that are received over the subscribed exchange and queue.
        channel (BlockingChannel | None): optional existing (open) RabbitMQ channel to reuse.
            Default is to create unique channel for this consumer.

    Returns:
        tuple[BlockingConnection, BlockingChannel]: the connection and channel, which are now open
            and subscribed to the provided queue.
    """
    _connection, _channel, queue_name = _initialize_connection_and_channel(
        connection, rmq_params, channel
    )

    # begin consuming messages
    auto_ack = queue_name == DIRECT_REPLY_QUEUE
    logger.info('Consuming messages from queue %s with auto_ack: %s', queue_name, auto_ack)

    _channel.basic_qos(prefetch_count=1)
    _channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback,
                           auto_ack=auto_ack)
    return _connection, _channel


def _setup_exch_and_queue(channel: Channel, exch: Exch, queue: Queue):
    """Setup an exchange and queue and bind them with the queue's route key(s)"""
    if queue.arguments and 'x-queue-type' in queue.arguments and \
       queue.arguments['x-queue-type'] == 'quorum' and queue.auto_delete:
        raise ValueError('Quorum queues can not be configured to auto delete')

    _setup_exch(channel, exch)

    result: Method = channel.queue_declare(
        queue=queue.name,
        exclusive=queue.exclusive,
        durable=queue.durable,
        auto_delete=queue.auto_delete,
        arguments=queue.arguments
    )
    queue_name = result.method.queue
    logger.debug('Declared queue: %s', queue_name)

    if isinstance(queue.route_key, list):
        for route_key in queue.route_key:
            channel.queue_bind(
                queue_name,
                exchange=exch.name,
                routing_key=route_key
            )
            logger.debug('Bound queue(%s) to exchange(%s) with route_key(%s)',
                         queue_name, exch.name, route_key)
    else:
        channel.queue_bind(
            queue_name,
            exchange=exch.name,
            routing_key=queue.route_key
        )
        logger.debug('Bound queue(%s) to exchange(%s) with route_key(%s)',
                     queue_name, exch.name, queue.route_key)


def _setup_exch(channel: Channel, exch: Exch):
    """Setup and exchange"""
    channel.exchange_declare(
        exchange=exch.name,
        exchange_type=exch.type,
        durable=exch.durable
    )
    logger.debug('Declared exchange: %s', exch.name)


def threadsafe_call(channel: Channel, *functions: Callable):
    """
    This function provides a thread safe way to call pika functions (or functions that call
    pika functions) from a thread other than the main. The need for this utility is practice of
    executing function/method and separate thread to avoid blocking the rabbitMQ heartbeat
    messages send by pika from the main thread.

    Note: that `channel` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).

    Examples:
        # Simple ack a message
        threadsafe_call(self.channel,
                        partial(self.channel.basic_ack,
                                delivery_tag=delivery_tag))

        # RPC response followed and nack without requeueing
        response = {'Error': 'Invalid request'}
        threadsafe_call(self.channel,
                        partial(self.channel.basic_publish,
                                exchange='',
                                routing_key=response_props.reply_to,
                                properties=response_props,
                                body=json.dumps(response)),
                        partial(channel.basic_nack,
                                delivery_tag=delivery_tag,
                                requeue=False))

        # Publishing message via the PublishConfirm utility
        threadsafe_call(self.pub_conf.channel,
                        partial(self.pub_conf.publish_message,
                                message=message))
    Args:
        channel (BlockingChannel): RabbitMQ channel.
        functions (Callable): One or more callable function, typically created via
                                functools.partial or lambda, but can be function without args
    """
    def call_if_channel_is_open():
        if channel.is_open:
            for func in functions:
                func()
        else:
            logger.error('Channel closed before callback could be run')
            raise ConnectionError('RabbitMQ Channel is closed')
    channel.connection.add_callback_threadsafe(call_if_channel_is_open)


def threadsafe_ack(
        channel: Channel,
        delivery_tag: int,
        extra_func: Callable = None,
):
    """
    This is just a convenance function that acks a message via threadsafe_call

    Args:
        channel (BlockingChannel): RabbitMQ channel.
        delivery_tag (int): Delivery tag to be used when nacking.
        extra_func (Callable): Any extra function that you would like to be called after the nack.
                               Typical use case would we to send a log via a lambda
                               (e.g. extra_func = lambda: logger.debug('Message has been nacked')).
    """
    if extra_func:
        threadsafe_call(channel, lambda: channel.basic_ack(delivery_tag), extra_func)
    else:
        threadsafe_call(channel, lambda: channel.basic_ack(delivery_tag))


def threadsafe_nack(
        channel: Channel,
        delivery_tag: int,
        extra_func: Callable = None,
        requeue: bool = False,
):
    """
    This is just a convenance function that nacks a message via threadsafe_call

    Args:
        channel (BlockingChannel): RabbitMQ channel.
        delivery_tag (int): Delivery tag to be used when nacking.
        extra_func (Callable): Any extra function that you would like to be called after the nack.
                               Typical use case would we to send a log via a lambda
                               (e.g. extra_func = lambda: logger.debug('Message has been nacked')).
        requeue (bool, optional): Indication if the message should be re-queued. Defaults to False.
    """
    if extra_func:
        threadsafe_call(channel,
                        lambda: channel.basic_nack(delivery_tag, requeue=requeue),
                        extra_func)
    else:
        threadsafe_call(channel, lambda: channel.basic_nack(delivery_tag, requeue=requeue))


def _set_context(context):
    for var, value in context.items():
        var.set(value)


class Consumer(Thread):
    """
    RabbitMQ consumer, runs in own thread to not block heartbeat. A thread pool
    is used to not so much to parallelize the execution but rather to manage the
    execution of the callbacks, including being able to wait for completion on
    shutdown.  The start() and stop() methods should be called from the same
    thread as the one used to create the instance.
    """

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    def __init__(
        self,
        conn_params: Conn,
        rmq_params_and_callbacks: RabbitMqParamsAndCallback | list[RabbitMqParamsAndCallback],
        num_message_handlers: int,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.context = contextvars.copy_context()
        self.daemon = True
        self._tpx = ThreadPoolExecutor(max_workers=num_message_handlers)
        self._conn_params = conn_params
        if isinstance(rmq_params_and_callbacks, list):
            self._rmq_params_and_callbacks = rmq_params_and_callbacks
        else:
            self._rmq_params_and_callbacks = [rmq_params_and_callbacks]
        self.connection = BlockingConnection(self._conn_params.connection_parameters)
        self.channel = self.connection.channel()

        self._consumer_tags = []
        for (exch, queue), func in self._rmq_params_and_callbacks:
            _setup_exch_and_queue(self.channel, exch, queue)
            self._consumer_tags.append(
                self.channel.basic_consume(queue.name,
                                           partial(self._on_message, func=func))
            )

        self.channel.basic_qos(prefetch_count=1)

    def run(self):
        _set_context(self.context)
        logger.info('Start Consuming...  (to stop press CTRL+C)')
        self.channel.start_consuming()

    def stop(self):
        """Cleanly end the running of a thread, free up resources"""
        logger.info('Stopping consumption of messages...')
        logger.debug('Waiting for any currently running workers (this could take some time)')
        self._tpx.shutdown(wait=True, cancel_futures=True)
        # it would be nice to stop consuming before shutting down the thread pool, but when done in
        # in the other order completed tasks can't be (n)ack-ed, this does mean that messages can be
        # consumed from the queue and the shutdown starts that will not be processed, nor (n)ack-ed

        if self.connection and self.connection.is_open:
            # there should be one consumer tag for each channel being consumed from
            if self._consumer_tags:
                threadsafe_call(self.channel,
                                *[partial(self.channel.stop_consuming, consumer_tag)
                                  for consumer_tag in self._consumer_tags],
                                lambda: logger.info('Stopped Consuming'))

            threadsafe_call(self.channel,
                            self.channel.close,
                            self.connection.close)

    # pylint: disable=too-many-arguments
    def _on_message(self, channel, method, properties, body, func):
        """This is the callback wrapper, the core callback is passed as func"""
        try:
            self._tpx.submit(func, channel, method, properties, body)
        except RuntimeError as exe:
            logger.error('Unable to submit it to thread pool, Cause: %s', exe)


class Publisher(Thread):
    """
    RabbitMQ publisher, runs in own thread to not block heartbeat. The start() and stop()
    methods should be called from the same thread as the one used to create the instance.
    """
    def __init__(
        self,
        conn_params: Conn | Channel,
        exch_params: Exch,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.context = contextvars.copy_context()
        self.daemon = True
        self._is_running = True
        self._exch = exch_params
        self._queue = None

        if isinstance(conn_params, Conn):
            # create new RabbitMQ Connection and Channel using the provided params
            self.connection = BlockingConnection(conn_params.connection_parameters)
            self.channel = self.connection.channel()
        elif isinstance(conn_params, Channel):
            # reuse the existing RabbitMQ Channel (and its connection) passed to Publisher()
            self.connection = conn_params.connection
            self.channel = conn_params
        else:
            raise ValueError('Publisher expects RabbitMQ params (Conn) or existing Channel to run setup')

        # if delivery is mandatory there must be a queue attach to the exchange
        if self._exch.mandatory:
            self._queue = Queue(name=f'_{self._exch.name}_{uuid.uuid4()}',
                                route_key=self._exch.route_key,
                                durable=False,
                                exclusive=True,
                                auto_delete=False,
                                arguments={'x-queue-type': 'classic',
                                           'x-message-ttl': 10 * 1000})

            _setup_exch_and_queue(self.channel, self._exch, self._queue)
        else:
            _setup_exch(self.channel, self._exch)

        if self._exch.delivery_conf:
            self.channel.confirm_delivery()

    def run(self):
        _set_context(self.context)
        logger.info('Starting publisher')
        while self._is_running:
            if self.connection and self.connection.is_open:
                self.connection.process_data_events(time_limit=1)

    def publish(self, message: bytes, properties: BasicProperties = None, route_key: str = None):
        """
        Publish a message to this pre configured exchange. The actual publication
        is asynchronous and this method only schedules it to be done.

        Args:
            message (bytes): The message to be published
            properties (BasicProperties): The props to be attached to message when published
            route_key (str): Optional route key, overriding key provided during initialization
        """
        threadsafe_call(self.channel,
                        lambda: self._publish(message, properties, route_key, [False]))

    def blocking_publish(self,
                         message: bytes,
                         properties: BasicProperties = None,
                         route_key: str = None) -> bool:
        """
        Blocking publish. Works by waiting for the completion of an asynchronous
        publication.

        Args:
            message (bytes): The message to be published
            properties (BasicProperties): The props to be attached to message when published
            route_key (str): Optional route key, overriding key provided during initialization

        Returns:
            bool: Returns True if no errors ocurred during publication. If this
                  publisher is configured to confirm delivery will return False if
                  failed to confirm.
        """
        success_flag = [False]
        done_event = Event()
        threadsafe_call(self.channel, lambda: self._publish(message,
                                                            properties,
                                                            route_key,
                                                            success_flag,
                                                            done_event))
        done_event.wait()
        return success_flag[0]

    def stop(self):
        """Cleanly end the running of a thread, free up resources"""
        logger.info("Stopping publisher")
        self._is_running = False
        # Wait until all the data events have been processed
        if self.connection and self.connection.is_open:
            self.connection.process_data_events(time_limit=1)
            threadsafe_call(self.channel,
                            self.channel.close,
                            self.connection.close)

    # pylint: disable=too-many-arguments,unused-argument
    def _publish(
            self,
            message: bytes,
            properties: BasicProperties,
            route_key: str = None,
            success_flag: list[bool] = None,
            done_event: Event = None
    ):
        """
        Core publish method. Success flag is passed by reference, and done event, if not None
        can be used to block until message is actually publish, vs being scheduled to be.

        success_flag (list[bool]): This is effectively passing a boolean by reference. This
                                   will change the value of the first element it this list
                                   to indicate if the core publishing was successful.
        done_event (Event): A Thread.Event that can be used to indicate when publishing is
                           complete in a different thread. This can be used to wait for the
                           completion via 'done_event.wait()' following calling this function.
        """
        if success_flag:
            success_flag[0] = False
        try:
            self.channel.basic_publish(self._exch.name,
                                       route_key if route_key else self._exch.route_key,
                                       body=message,
                                       properties=properties,
                                       mandatory=self._exch.mandatory)
            if success_flag:
                success_flag[0] = True
            if self._queue and self._queue.name.startswith('_'):
                try:
                    self.channel.queue_purge(queue=self._queue.name)
                except ValueError as exe:
                    logger.warning('Exception when removing message from private queue: %s', exe)
        except UnroutableError:
            logger.warning('Message was not delivered')
        except Exception as exe:
            logger.warning('Message not published, cause: %s', exe)
            raise exe
        finally:
            if done_event:
                done_event.set()


class Rpc:
    """
    RabbitMQ RPC (remote procedure call) client, runs in own thread to not block heartbeat.
    The start() and stop() methods should be called from the same thread that created the instance.

    This RPC class can be used to send "requests" (outbound messages) over RabbitMQ and block until
    a "response" (inbound message) comes back from the receiving app. All consuming and producing is
    of different queues and matching up requests with responses is abstracted away.

    Example usage:

        my_client = RpcClient(...insert params here...)

        response = my_client.send_message('{"some": "json"}')  # blocks while waiting for response

        logger.info(f'Response from external service: {response}')

    Args:
        conn_params (Conn): parameters to connect to RabbitMQ server
        publish_params (Exch): parameters of RMQ Exchange where messages should be sent
        consume_params (RabbitMqParams): parameters of RMQ Exchange/Queue to receive responses over
            from the external RabbitMQ service
        timeout (float  | None): optional timeout to give up on receiving each response.
            Default is None, meaning wait indefinitely for response from external service
    """
    def __init__(self, conn_params: Conn, exch: Exch, timeout: float | None = None):
        #  consume_params: RabbitMqParams,  # TODO: is this ok to be hard-coded?
        # self._consume_params = consume_params
        self._publish_params = exch
        self._timeout = timeout

        # worklist to track corr_ids sent to remote service, and associated response when it arrives
        self._pending_requests: dict[str, Future] = {}

        # Start long-running thread to consume any messages from response queue
        self._consumer = Consumer(
            conn_params,
            RabbitMqParamsAndCallback(RabbitMqParams(
                Exch('', 'direct'),
                Queue(DIRECT_REPLY_QUEUE, '', True, False, False)
            ), self._response_callback),
            num_message_handlers=2
        )
        # Publisher relies on Consumer to reuse RabbitMQ channel (required by Direct Reply-To)
        self._publisher = Publisher(conn_params, exch, channel=self._consumer.channel)
        # self._publisher.channel.basic_consume(DIRECT_REPLY_QUEUE, self._response_callback, False, False)

    @property
    def is_open(self) -> bool:
        """Returns True if RabbitMQ connection (Publisher) is open and ready to send messages"""
        # TODO: will this work?
        return self._consumer.is_alive() and self._publisher.is_alive()

    def send_request(self, request_body: str | bytes) -> str | None:
        """Send message to remote RabbitMQ service using thread-safe RPC. Will block until response
        is received back, or timeout occurs.

        Returns:
            Json | None: The response JSON, or None on timeout or error handling response
        """
        if not self.is_open:
            logger.debug('RPC thread not yet initialized. Setting up now')
            self.start()

        # block until thread has connected channel
        # TODO: this sleep is not threadsafe, not gonna fly
        # while not self.is_open:
        #     from time import sleep
        #     sleep(0.01)

        # generate unique ID to associate our request to data service's response
        request_id = str(uuid.uuid4())

        # send request to data service, providing the queue where it should respond
        properties = BasicProperties(
            content_type='application/json',
            correlation_id=request_id,
            reply_to=DIRECT_REPLY_QUEUE,   # reply_to=self._consume_params.queue.name,
        )

        # add future to dict where callback can retrieve it and set result
        request_future = Future()
        self._pending_requests[request_id] = request_future

        # TODO: Direct-reply messages must be published and consumed by the same connection &
        # channel (which are unique per Thread)
        logger.debug('Publishing request message to data service with body: %s', request_body)
        self._publisher.blocking_publish(request_body,
                                         properties=properties,
                                         route_key=self._publish_params.route_key)

        try:
            # block until callback runs (we'll know when the future's result has been changed)
            return request_future.result(timeout=self._timeout)
        except TimeoutError:
            logger.warning('Timed out waiting for data service response. correlation_id: %s',
                           request_id)
            return None
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning('Unexpected response from data service: %s', str(exc))
            return None

    def start(self):
        """Start dedicated threads to asynchronously send and receive RPC messages using a new
        RabbitMQ connection and channel. Note: this method can be called externally, but it is
        not required to use the client. It will automatically call this internally as needed."""
        if not self.is_open:
            logger.debug('Starting RPC threads to send and consume messages')
            self._consumer.start()
            self._publisher.start()

    def stop(self):
        """Unsubscribe to data service response queue and cleanup thread"""
        logger.debug('Shutting down RPC threads')
        if not self.is_open:
            logger.debug('RPC threads not running, nothing to cleanup')
            return

        # tell Consumer & Publisher to cleanup RabbitMQ resources; wait for their threads to terminate
        self._consumer.stop()
        self._publisher.stop()
        self._consumer.join()
        self._publisher.join()

    def _response_callback(self,
                           channel: Channel,
                           method: Basic.Deliver,
                           properties: BasicProperties,
                           body: bytes):
        """Handle RabbitMQ message emitted to response queue."""
        logger.info('Received response message with routing_key: %s, content_type: %s, size: %i',
                    method.routing_key, properties.content_type, len(body))
        logger.debug('Received message: %s', str(body))

        is_direct_reply = str(method.routing_key).startswith(DIRECT_REPLY_QUEUE)

        # remove future from pending list. we will update result shortly
        request_future = self._pending_requests.pop(properties.correlation_id)

        # TODO: should RPC only work for JSON messages? IDSSe services expect it, but will that ever change?
        # require message to be json before attempting to parse
        if properties.content_type != 'application/json':
            logger.warning('Received unsupported message type: %s', properties.content_type)

            # messages sent through RabbitMQ Direct reply-to are auto acked, don't attempt to nack
            if not is_direct_reply:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            return request_future.set_exception(TypeError('Response was not application/json'))

        # messages sent through RabbitMQ Direct reply-to are auto acked
        if not is_direct_reply:
            channel.basic_ack(delivery_tag=method.delivery_tag)

        # update future with response body to communicate it across to main thread
        return request_future.set_result(body)
