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

import logging
import logging.config
import uuid
from concurrent.futures import ThreadPoolExecutor
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
    delivery_conf: bool | None = None
    mandatory: bool | None = None


class Queue(NamedTuple):
    """An internal data class for holding the RabbitMQ queue info"""
    name: str
    route_key: str
    durable: bool
    exclusive: bool
    auto_delete: bool
    type: str = 'classic'


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
    arguments = {'x-message-ttl': 10 * 1000} if queue.name.startswith('_') else None
    frame: Method = channel.queue_declare(
        queue=queue.name,
        exclusive=queue.exclusive,
        durable=queue.durable,
        auto_delete=queue.auto_delete,
        arguments=arguments
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
    if not isinstance(connection, Conn):
        # connection of unsupported type passed
        raise ValueError(
            (f'Cannot use or create new RabbitMQ connection using type {type(connection)}. '
             'Should a Conn (a dict with connection parameters)')
        )
    """Establish RabbitMQ connection, and declare exchange and queue on new Channel"""
    _connection = BlockingConnection(parameters=connection)
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
    if queue.type == 'quorum' and queue.auto_delete:
        raise ValueError('Quorum queues can not be configured to auto delete')

    _setup_exch(channel, exch)

    result: Method = channel.queue_declare(
        queue=queue.name,
        exclusive=queue.exclusive,
        durable=queue.durable,
        auto_delete=queue.auto_delete,
        arguments={'x-queue-type': queue.type}
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


def threadsafe_nack(channel: Channel, delivery_tag: int, message: str, requeue: bool = False):
    """
    This is just a convenance function that nacks a message via threadsafe_call

    Args:
        channel (BlockingChannel): RabbitMQ channel.
        delivery_tag (int): Delivery tag to be used when nacking.
        message (str): The consumed message as a string
        requeue (bool, optional): Indication if the message should be re-queued. Defaults to False.
    """
    threadsafe_call(channel,
                    lambda: channel.basic_nack(delivery_tag, requeue=requeue),
                    lambda: logger.debug('Message has been nacked:\n%s', message))


class Consumer(Thread):
    """
    RabbitMQ consumer, runs in own thread to not block heartbeat. A thread pool
    is used to not so much to parallelize the execution but rather to manage the
    execution of the callbacks, including being able to wait for completion on
    shutdown.  The start() and stop() methods should be called from the same
    thread as the one used to create the instance.
    """
    def __init__(
        self,
        conn_params: ConnectionParameters,
        rmq_params_and_callbacks: RabbitMqParamsAndCallback | list[RabbitMqParamsAndCallback],
        num_message_handlers: int,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self._tpx = ThreadPoolExecutor(max_workers=num_message_handlers)
        self._conn_params = conn_params
        if isinstance(rmq_params_and_callbacks, list):
            self._rmq_params_and_callbacks = rmq_params_and_callbacks
        else:
            self._rmq_params_and_callbacks = [rmq_params_and_callbacks]
        self.connection = BlockingConnection(parameters=self._conn_params)
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
        conn_params: ConnectionParameters,
        exch_params: Exch,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self._is_running = True
        self._exch = exch_params
        self._queue = None

        self.connection = BlockingConnection(conn_params)
        self.channel = self.connection.channel()

        # if delivery is mandatory there must be a queue attach to the exchange
        if self._exch.mandatory:
            self._queue = Queue(name=f'_{self._exch.name}_{uuid.uuid4()}',
                                route_key=self._exch.route_key,
                                durable=False,
                                exclusive=True,
                                auto_delete=False)

            _setup_exch_and_queue(self.channel, self._exch, self._queue)
        else:
            _setup_exch(self.channel, self._exch)

        if self._exch.delivery_conf:
            self.channel.confirm_delivery()

    def run(self):
        logger.info('Starting publisher')
        while self._is_running:
            self.connection.process_data_events(time_limit=1)

    def publish(self, message: bytes, properties: BasicProperties = None):
        """
        Publish a message to this pre configured exchange. The actual publication
        is asynchronous and this method only schedules it to be done.

        Args:
            message (bytes): The message to be published
            properties (BasicProperties): The props to be attached to message when published
        """
        threadsafe_call(self.channel, lambda: self._publish(message, properties, [False]))

    def blocking_publish(self, message: bytes, properties: BasicProperties = None) -> bool:
        """
        Blocking publish. Works by waiting for the completion of an asynchronous
        publication.

        Args:
            message (bytes): The message to be published
            properties (BasicProperties): The props to be attached to message when published

        Returns:
            bool: Returns True if no errors ocurred during publication. If this
                  publisher is configured to confirm delivery will return False if
                  failed to confirm.
        """
        success_flag = [False]
        done_event = Event()
        threadsafe_call(self.channel, lambda: self._publish(message,
                                                            properties,
                                                            success_flag,
                                                            done_event))
        done_event.wait()
        return success_flag[0]

    def stop(self):
        """Cleanly end the running of a thread, free up resources"""
        logger.info("Stopping publisher")
        self._is_running = False
        # Wait until all the data events have been processed
        self.connection.process_data_events(time_limit=1)
        if self.connection.is_open:
            threadsafe_call(self.channel,
                            self.channel.close,
                            self.connection.close)

    def _publish(
            self,
            message: bytes,
            properties: BasicProperties,
            success_flag: list[bool],
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
        success_flag[0] = False
        try:
            self.channel.basic_publish(self._exch.name,
                                       self._exch.route_key,
                                       body=message,
                                       properties=properties,
                                       mandatory=self._exch.mandatory)
            success_flag[0] = True
            print('\n message published\n')
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
