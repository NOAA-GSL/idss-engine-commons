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
from typing import Callable, NamedTuple, Optional, Tuple, Union

from pika import BasicProperties, ConnectionParameters, PlainCredentials
from pika.adapters import BlockingConnection, blocking_connection
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
    channel: blocking_connection.BlockingChannel,
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
        channel.exchange_declare(exchange=exch.name, exchange_type=exch.type)

    # Do not try to declare or bind built-in queues. They are pseudo-queues that already exist
    if queue.name.startswith('amq.rabbitmq.'):
        return queue.name

    frame: Method = channel.queue_declare(
        queue=queue.name,
        exclusive=queue.exclusive,
        durable=queue.durable,
        auto_delete=queue.auto_delete
    )

    # Bind queue to exchange with routing_key. May need to support multiple keys in the future
    if exch.name != '':
        logger.info('    binding key %s to queue: %s', queue.route_key, queue.name)
        channel.queue_bind(queue.name, exch.name, queue.route_key)
    return frame.method.queue


def subscribe_to_queue(
    connection: Union[Conn, BlockingConnection],
    params: RabbitMqParams,
    on_message_callback: Callable[
        [blocking_connection.BlockingChannel, Basic.Deliver, BasicProperties, bytes], None],
    channel: Optional[blocking_connection.BlockingChannel] = None
) -> Tuple[BlockingConnection, blocking_connection.BlockingChannel]:
    """
    Function that handles setup of consumer of RabbitMQ queue messages, declaring the exchange and
    queue if needed, and invoking the provided callback when a message is received.

    If an existing BlockingConnection or BlockingChannel are passed, they are used to
    setup the subscription, but by default a new connection and channel will be established and
    returned, which the caller can immediately begin doing RabbitMQ operations with.

    For example: start a blocking consume of messages with channel.start_consuming(), or
    close gracefully with connection.close()

    Args:
        connection (Union[Conn, BlockingConnection]): connection parameters to establish new
            RabbitMQ connection, or existing RabbitMQ connection to reuse for this consumer.
        params (RabbitMqParams): parameters for the RabbitMQ exchange and queue from which to
            to consume messages.
        on_message_callback (Callable[
            [BlockingChannel, Basic.Deliver, BasicProperties, bytes], None]):
            function to handle messages that are received over the subscribed exchange and queue.
        channel (Optional[BlockingChannel]): optional existing (open) RabbitMQ channel to reuse.
            Default is to create unique channel for this consumer.

    Returns:
        Tuple[BlockingConnection, BlockingChannel]: the connection and channel, which are now open
            and subscribed to the provided queue.
    """
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

    # begin consuming messages
    auto_ack = queue_name == DIRECT_REPLY_QUEUE
    logger.info('Consuming messages from queue %s with auto_ack: %s', queue_name, auto_ack)

    _channel.basic_qos(prefetch_count=1)
    _channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback,
                           auto_ack=auto_ack)
    return (_connection, _channel)
