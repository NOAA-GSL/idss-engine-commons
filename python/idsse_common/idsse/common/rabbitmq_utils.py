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

import json
import logging
import logging.config
from collections.abc import Callable
from typing import NamedTuple

from pika import BasicProperties, ConnectionParameters, PlainCredentials
from pika.adapters import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.channel import Channel
from pika.exceptions import AMQPConnectionError
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

    def to_connection(self) -> BlockingConnection:
        """Establish a new RabbitMQ connection using attributes in Conn data class

        Returns:
           BlockingConnection: newly established instance of pika.BlockingConnection
        """
        return BlockingConnection(parameters=self.connection_parameters)

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
    durable: bool = True


class Queue(NamedTuple):
    """An internal data class for holding the RabbitMQ queue info"""
    name: str
    route_key: str
    durable: bool
    exclusive: bool
    auto_delete: bool


class RabbitMqParams(NamedTuple):
    """Data class to hold configurations for RabbitMQ exchange/queue pair"""
    exchange: Exch
    queue: Queue


def _initialize_exchange_and_queue(
    channel: BlockingChannel,
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
        channel.exchange_declare(exchange=exch.name, exchange_type=exch.type, durable=exch.durable)

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
    connection: Conn | BlockingConnection,
    params: RabbitMqParams,
    channel: BlockingChannel | Channel | None = None,
) -> tuple[BlockingConnection, Channel, str]:
    """Establish (or reuse) RabbitMQ connection, and declare exchange and queue on new Channel"""
    if isinstance(connection, Conn):
        # Use connection as parameters to establish new connection
        _connection = connection.to_connection()
        logger.info('Established new RabbitMQ connection to %s on port %i',
                    connection.host, connection.port)
    elif isinstance(connection, BlockingConnection):
        # Or existing open connection was provided, so use that
        _connection = connection
    else:
        # connection of unsupported type passed
        raise ValueError(
            (f'Cannot use or create new RabbitMQ connection using type {type(connection)}. '
             'Should be one of: [Conn, pika.BlockingConnection]')
        )

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
        [BlockingChannel, Basic.Deliver, BasicProperties, bytes], None],
    channel: BlockingChannel | None = None
) -> tuple[BlockingConnection, BlockingChannel]:
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


def threadsafe_call(connection, channel, *partial_functions):
    """This function provides a thread safe way to call pika functions (or functions that call
    pika functions) from a thread other than the main. The need for this utility is practice of
    executing function/method and separate thread to avoid blocking the rabbitMQ heartbeat
    messages send by pika from the main thread.

    Note: that `channel` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).

    Examples:
        # Simple ack a message
        threadsafe_call(self.connection, self.channel,
                        partial(self.channel.basic_ack,
                                delivery_tag=delivery_tag))

        # RPC response followed and nack without requeueing
        response = {'Error': 'Invalid request'}
        threadsafe_call(self.connection, self.channel,
                        partial(self.channel.basic_publish,
                                exchange='',
                                routing_key=response_props.reply_to,
                                properties=response_props,
                                body=json.dumps(response)),
                        partial(channel.basic_nack,
                                delivery_tag=delivery_tag,
                                requeue=False))

        # Publishing message via the PublishConfirm utility
        threadsafe_call(self.connection, self.pub_conf.channel,
                        partial(self.pub_conf.publish_message,
                                message=message))
    Args:
        connection (BlockingConnection): RabbitMQ connection.
        channel (BlockingChannel): RabbitMQ channel.
        partial_functions (Callable): One or more callable function (typically created via
        functools.partial)
    """
    def call_if_channel_is_open():
        if channel.is_open:
            for func in partial_functions:
                func()
        else:
            logger.error('Channel closed before callback could be run')
            raise ConnectionError('RabbitMQ Channel is closed')
    connection.add_callback_threadsafe(call_if_channel_is_open)


class PublisherSync:
    """
    Uses a synchronous, blocking RabbitMQ connection to publish messages (no thread safety
    or multithreading support). It's recommended that you gracefully close the connection when
    you're done with it using close().

    Args:
        conn_params (Conn): connection parameters to establish a new
            RabbitMQ connection
        rmq_params (RabbitMqParams): parameters for RabbitMQ exchange and queue on which to publish
            messages
    """
    def __init__(
        self,
        conn_params: Conn,
        rmq_params: RabbitMqParams,
        channel: Channel | None = None,

    ) -> tuple[BlockingConnection, Channel]:
        # save params
        self._conn_params = conn_params
        self._rmq_params = rmq_params

        # establish BlockingConnection and declare exchange and queue on Channel
        self._connection, self._channel, self._queue_name = _initialize_connection_and_channel(
            conn_params, rmq_params, channel,
        )

        self._channel.confirm_delivery()  # enable delivery confirmations from RabbitMQ broker

    def stop(self):
        """Cleanly close ("stop") any open RabbitMQ connection and channel. This has the same
        functionality as close(), it's just to match the interface of ```PublishConfirm```"""
        self.close()

    def close(self):
        """Cleanly close any open RabbitMQ connection and channel"""
        def _close_connection():
            if self._channel:
                self._channel.close()
            self._connection.close()

        self._connection.add_callback_threadsafe(_close_connection)

    def publish_message(self, message: dict, routing_key='', corr_id: str | None = None) -> bool:
        """Publish a message to the RabbitMQ queue. Non-blocking, and no delivery confirmation.
        Returns False if message is invalid or could not be sent, but otherwise no validation.

        Args:
            message (dict): message to publish. Must be valid JSON dictionary.
            routing_key (str, optional): routing_key to route the message to correct consumer.
                Defaults to ''.
            corr_id (str | None, optional): correlation_id to tag message. Defaults to None.

        Returns:
            bool: True if message was published to the queue
        """

        properties = BasicProperties(content_type='application/json',
                                     content_encoding='utf-8',
                                     correlation_id=corr_id)
        try:
            self._channel.basic_publish(self._rmq_params.exchange.name, routing_key,
                                        json.dumps(message, ensure_ascii=True), properties)

            return True
        except AMQPConnectionError:  # pylint: disable=broad-exception-caught
            try:
                self._connection, self._channel, self._queue_name = \
                    _initialize_connection_and_channel(self._conn_params, self._rmq_params)
                self._channel.basic_publish(self._rmq_params.exchange.name, routing_key,
                                            json.dumps(message, ensure_ascii=True), properties)

                return True
            except AMQPConnectionError as exc:  # pylint: disable=broad-exception-caught
                logger.error('Publish message problem: [%s] %s', type(exc), str(exc))
                return False
