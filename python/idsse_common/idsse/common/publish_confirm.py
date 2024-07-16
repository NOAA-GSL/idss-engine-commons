"""Module for PublishConfirm threaded RabbitMQ publisher"""
# ----------------------------------------------------------------------------------
# Created on Fri Jun 23 2023.
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Geary Layne (1)
#     Paul Hamer (2)
#     Mackenzie Grimes (2)
# ----------------------------------------------------------------------------------
# pylint: disable=C0111,C0103,R0205

import functools
import logging
import logging.config
import json
import time
from concurrent.futures import Future
from dataclasses import dataclass, field
from random import randint
from threading import Thread
from typing import NamedTuple, cast

from pika import SelectConnection, BasicProperties
from pika.channel import Channel
from pika.frame import Method
from pika.spec import Basic

from idsse.common.rabbitmq_utils import Conn, Exch, Queue

logger = logging.getLogger(__name__)


@dataclass
class PublishConfirmRecords:
    """Data class to track RabbitMQ activity metadata

    Args:
        deliveries (dict[int, str]): mapping of delivered message IDs to message content
        acked (int): Count of acknowledged RabbitMQ messages
        nacked (int): Count of unacknowledged RabbitMQ messages
        message_number (int): The ID which will be assigned to the next published message
    """
    deliveries: dict[int, str] = field(default_factory=dict)
    acked: int = 0
    nacked: int = 0
    message_number: int = 0


class PublishConfirmParams(NamedTuple):
    """Data class to hold RabbitMQ configurations for PublishConfirm"""
    conn: Conn
    exchange: Exch
    queue: Queue


class PublishConfirm:
    """This is a publisher that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures for any process.
    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.
    """

    def __init__(self, conn: Conn, exchange: Exch, queue: Queue):
        """Setup the example publisher object, passing in the RabbitMqUtils we will use to
        connect to RabbitMQ.

        Args:
            conn (Conn): The RabbitMQ connection detail object
            exchange (Exch): The RabbitMQ exchange details.
            queue (Queue): The RabbitMQ queue details. If name starts with '_', will be setup as
                a "private queue", i.e. not intended for consumers, and all published messages
                will have a 10-second TTL.
        """
        self._thread = Thread(name=f'PublishConfirm-{randint(0, 9)}',
                              daemon=True,
                              target=self._run)

        self._connection: SelectConnection | None = None
        self._channel: Channel | None = None

        self._stopping = False
        self._rmq_params = PublishConfirmParams(conn, exchange, queue)

        self._records = PublishConfirmRecords()  # data class to track message activity
        self._is_ready_future: Future | None = None

    def publish_message(self,
                        message: dict,
                        routing_key='',
                        corr_id: str | None = None) -> bool:
        """If the class is not stopping, publish a message to RabbitMQ,
        appending a list of deliveries with the message number that was sent.
        This list will be used to check for delivery confirmations in the
        on_delivery_confirmations method.

        Args:
            message (dict): message to publish (should be valid json)
            routing_key (str): routing_key to route the message to correct consumer.
                Default is empty str
            corr_id (str | None): optional correlation_id to include in message

        Returns:
            bool: True if message successfully published to queue (channel was open and
                publish did not throw exception)
        Raises:
            RuntimeError: if channel is uninitialized (start() not completed yet) or is closed
        """
        is_ready = self._wait_for_channel_to_be_ready()
        if not is_ready:
            logger.error('RabbitMQ channel not established for some reason. Cannnot publish')
            return False

        logger.info('DEBUG: channel is ready to publish message')

        try:
            properties = BasicProperties(content_type='application/json',
                                         content_encoding='utf-8',
                                         correlation_id=corr_id)

            logger.info('Publishing message to queue %s, message length: %d',
                        self._rmq_params.queue.name, len(json.dumps(message)))
            self._channel.basic_publish(self._rmq_params.exchange.name, routing_key,
                                        json.dumps(message, ensure_ascii=True),
                                        properties)
            self._records.message_number += 1
            self._records.deliveries[self._records.message_number] = message
            logger.info('Published message # %i to exchange %s, queue %s, routing_key %s',
                         self._records.message_number, self._rmq_params.exchange.name,
                         self._rmq_params.queue.name, routing_key)
            return True

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error('Publish message problem : (%s) %s', type(e), str(e))
            return False

    def start(self):
        """Start thread to connect to RabbitMQ queue and prepare to publish messages, invoking
        callback when setup complete.

        Raises:
            RuntimeError: if PublishConfirm thread is already running
        """
        logger.debug('Starting thread')

        # not possible to start Thread when it's already running
        if self._thread.is_alive() or (self._connection is not None and self._connection.is_open):
            raise RuntimeError('PublishConfirm thread already running, cannot be started')
        self._start()

    def stop(self):
        """Stop the example by closing the channel and connection. We
        set a flag here so that we stop scheduling new messages to be
        published. The IOLoop is started because this method is
        invoked by the Try/Catch below when KeyboardInterrupt is caught.
        Starting the IOLoop again will allow the publisher to cleanly
        disconnect from RabbitMQ.
        """
        logger.info('Stopping')
        self._stopping = True
        self._close_connection()
        self._stopping = False  # done stopping

    def _run(self):
        """Run a new thread: get a new RMQ connection, and start looping until stop() is called"""
        self._connection = self._create_connection()
        self._connection.ioloop.start()
        time.sleep(0.2)

        while not self._stopping:
            time.sleep(.1)

        if self._connection is not None and not self._connection.is_closed:
            # Finish closing
            self._connection.ioloop.start()

    def _start(self, is_ready: Future | None = None):
        """
        Start a thread to handle PublishConfirm operations

        Args:
            on_ready (Future | None): optional Python Future that will be resolved
                once instance is ready to publish messages (all RabbitMQ connection and channel
                are set up, delivery confirmation is enabled, etc.), or raise an exception
                if some issue is encountered in that process. Defaults to None.
        """
        logger.debug('Starting thread with callback')
        if is_ready is not None:
            self._is_ready_future = is_ready  # to be invoked after all pika setup is done
        self._thread.start()

    def _create_connection(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        conn = self._rmq_params.conn
        logger.debug('Connecting to RabbitMQ: %s', conn)
        return SelectConnection(
            parameters=conn.connection_parameters,
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
            on_close_callback=self._on_connection_closed)

    def _wait_for_channel_to_be_ready(self, timeout: float | None = 6) -> bool:
        """If connection or channel are not open, start the PublishConfirm to do needed
        RabbitMQ setup. This method will not return until channel is confirmed ready for use,
        or timeout is exceeded.

        Args:
            timeout (optional, float): Duration of time, in seconds, to wait for RabbitMQ
                connection, channel, exchange and queue to be setup and ready to send messages.
                If timeout is None, thread will wait indefinitely. Default is 6 seconds.

        Returns:
            bool: True if channel is ready. False if timed out waiting for RabbitMQ to connect
        """

        # validate that PublishConfirm thread has been set up and connected to RabbitMQ
        logger.info('DEBUG _wait_for_channel_to_be_ready state')
        logger.info(self._connection)
        logger.info(self._channel)
        logger.info('----------------------')
        if (self._connection and self._connection.is_open
            and self._channel and self._channel.is_open):
            return True  # channel is already ready, nothing to do

        logger.info('Channel is not ready to publish, calling _start() now')

        # pass callback to flip is_ready flag, and block until flag changes
        is_ready_future = Future()

        logger.info('calling _start() with callback')
        self._start(is_ready=is_ready_future)

        logger.info('waiting for is_ready flag to be set')
        try:
            is_ready_future.result(timeout=timeout)
            logger.info('Connection and channel setup complete, ready to publish message')
            return True
        except TimeoutError:
            logger.error('Timed out waiting for RabbitMQ connection, channel, or exchange')
            return False
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error('RabbitMQ rejected connection for some reason: %s', str(exc))
            return False

    def _on_connection_open(self, connection: SelectConnection):
        """This method is called by pika once the connection to RabbitMQ has been established.

        Args:
            connection (SelectConnection): The connection
        """
        logger.debug('Connection opened. Creating a new channel')

        # Create a new channel.
        # When RabbitMQ confirms the channel is open by sending the Channel.OpenOK RPC reply,
        # the on_channel_open method will be invoked.
        connection.channel(on_open_callback=self._on_channel_open)

    def _on_connection_open_error(self, connection: SelectConnection, err: Exception):
        """This method is called by pika if the connection to RabbitMQ can't be established.

        Args:
            connection (SelectConnection): The connection
            err (Exception): The error
        """
        logger.error('Connection open failed, reopening in 5 seconds: %s', err)
        connection.ioloop.call_later(5, connection.ioloop.stop)

    def _on_connection_closed(self, connection: SelectConnection, reason: Exception):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        Args:
            connection (SelectConnection): The closed connection obj
            reason (Exception): exception representing reason for loss of connection.
        """
        self._channel = None

        if self._stopping:
            connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: %s', reason)
            connection.ioloop.call_later(5, connection.ioloop.stop)

    def _on_channel_open(self, channel: Channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it (declare the exchange to use).

        Args:
            channel (Channel): The channel object
        """
        logger.debug('Channel opened')
        self._channel = channel

        logger.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self._on_channel_closed)

        # Declare exchange on our new channel
        exch_name, exch_type, exch_durable = self._rmq_params.exchange  # pylint: disable=unused-variable
        logger.debug('Declaring exchange %s', exch_name)

        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(self._on_exchange_declareok, userdata=exch_name)
        try:
            self._channel.exchange_declare(exchange=exch_name,
                                       exchange_type=exch_type,
                                       callback=cb)
        except ValueError as exc:
            logger.warning('RabbitMQ failed to declare exchange: (%s) %s', type(exc), str(exc))
            if self._is_ready_future:
                self._is_ready_future.set_exception(exc)  # notify caller that we could not connect

    def _on_channel_closed(self, channel: Channel, reason: Exception):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        Args:
            channel (Channel): The closed channel
            reason (Exception): why the channel was closed
        """
        logger.warning('Channel %i was closed: %s', channel, reason)
        self._channel = None
        if not self._stopping:
            self._close_connection()

    def _on_exchange_declareok(self, _unused_frame: Method, userdata: str | bytes):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC command.

        Args:
            _unused_frame (Frame.Method): Exchange.DeclareOk response frame
            userdata (str | bytes): Extra user data (exchange name)
        """
        logger.debug('Exchange declared: %s', userdata)

        # Setup the queue on RabbitMQ by invoking the Queue.Declare RPC command. When it is
        # complete, the on_queue_declareok method will be invoked by pika.
        queue = self._rmq_params.queue
        logger.debug('Declaring queue %s', queue.name)

        # If we have a 'private' queue, i.e. one used to support message publishing, not consumed
        # Set message time-to-live (TTL) to 10 seconds
        args = {'x-message-ttl': 10 * 1000} if queue.name.startswith('_') else None

        if self._channel is not None:
            self._channel.queue_declare(queue=queue.name,
                                        durable=queue.durable,
                                        arguments=args,
                                        exclusive=queue.exclusive,
                                        auto_delete=queue.auto_delete,
                                        callback=self._on_queue_declareok)

    def _on_queue_declareok(self, _unused_frame: Method):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        Args:
            _unused_frame (Frame): The Queue.DeclareOk frame
        """
        _, exchange, queue = self._rmq_params
        logger.debug('Binding %s to %s with #', exchange.name, queue.name)

        if self._channel is not None:
            self._channel.queue_bind(queue.name,
                                     exchange.name,
                                     routing_key=queue.route_key,
                                     callback=self._on_bindok)

    def _on_bindok(self, _unused_frame: Method):
        """This method is invoked by pika when it receives the Queue.BindOk
        response from RabbitMQ. Since we know we're now setup and bound, it's
        time to start publishing."""
        logger.debug('Queue bound')

        # enable delivery confirmations and schedule the first message to be sent to RabbitMQ
        logger.debug('Issuing Confirm.Select RPC command')
        if self._channel is not None:
            self._records.deliveries[0] = 'Confirm.SelectOk'  # track the confirmation message
            self._channel.confirm_delivery(self._on_delivery_confirmation)

        # notify up that channel can now be published to
        if self._is_ready_future:
            self._is_ready_future.set_result(True)

        # self.schedule_next_message()

    def _on_delivery_confirmation(self, method_frame: Method):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing housekeeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        Args:
            method_frame (Method): Basic.Ack or Basic.Nack frame
        """
        # tell python type checker that method will be an Ack or Nack (per pika docs)
        method = cast(Basic.Ack | Basic.Nack, method_frame.method)

        confirmation_type = method.NAME.split('.')[1].lower()
        ack_multiple = method.multiple
        delivery_tag = method.delivery_tag

        logger.info('Received %s for delivery tag: %i (multiple: %s)',
                    confirmation_type, delivery_tag, ack_multiple)

        if confirmation_type == 'ack':
            self._records.acked += 1
        elif confirmation_type == 'nack':
            self._records.nacked += 1

        del self._records.deliveries[delivery_tag]

        if ack_multiple:
            for tmp_tag in list(self._records.deliveries.keys()):
                if tmp_tag <= delivery_tag:
                    self._records.acked += 1
                    del self._records.deliveries[tmp_tag]

        # NOTE: at some point we'd check self._deliveries for stale entries and attempt re-delivery
        logger.debug(
            'Published %i messages, %i have yet to be confirmed, %i were acked and %i were nacked',
            self._records.message_number,
            len(self._records.deliveries),
            self._records.acked,
            self._records.nacked)

    def _close_connection(self):
        """Close the connection to RabbitMQ (after closing any open channel on it)."""
        if self._channel is not None:
            logger.debug('Closing the channel')
            self._channel.close()

        if self._connection is not None:
            logger.debug('Closing connection')
            self._connection.close()
