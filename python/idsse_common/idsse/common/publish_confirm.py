"""Module for PublishConfirm threaded RabbitMQ publisher"""
# ----------------------------------------------------------------------------------
# Created on Fri Jun 23 2023.
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.  (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Geary Layne (1)
#     Paul Hamer (2)
# ----------------------------------------------------------------------------------
# pylint: disable=C0111,C0103,R0205

import functools
import logging
import logging.config
import json
import time
from dataclasses import dataclass, field
from threading import Thread
from typing import Optional, Dict

import pika
from pika import SelectConnection
from pika.exchange_type import ExchangeType
from pika.channel import Channel
from idsse.common.rabbitmq_utils import Conn, Exch, Queue
from idsse.common.log_util import get_default_log_config, set_corr_id_context_var

logger = logging.getLogger(__name__)


@dataclass
class PublishConfirmRecords:
    """Data class to track RabbitMQ activity metadata

    Args:
        deliveries (Dict[int, str]): mapping of delivered message IDs to message content
        acked (int): Count of acknowledged RabbitMQ messages
        nacked (int): Count of unacknowledged RabbitMQ messages
        message_number (int): The ID which will be assigned to the next published message
    """
    deliveries: Dict[int, str] = field(default_factory=dict)
    acked: int = 0
    nacked: int = 0
    message_number: int = 0


class PublishConfirm(Thread):
    """This is a publisher that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures for any process.
    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.
    """
    def __init__(self, conn: Conn, exchange: Exch, queue: Queue):
        """Setup the example publisher object, passing in the URL we will use
        to connect to RabbitMQ.
        :param Conn conn: The RabbitMQ connection detail object
        :param Exch exchange: The RabbitMQ exchange details
        :param Queue queue: The RabbitMQ queue details
        """
        super().__init__(daemon=True)

        self._connection: Optional[SelectConnection] = None
        self._channel: Optional[Channel] = None

        self._records = PublishConfirmRecords()

        self._stopping = False
        self._url = (f'amqp://{conn.username}:{conn.password}@{conn.host}'
                     f':{str(conn.port)}/%2F?connection_attempts=3&heartbeat=3600')
        self._exchange = exchange
        self._queue = queue

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        logger.info('Connecting to %s', self._url)
        return pika.SelectConnection(
            pika.URLParameters(self._url),
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
            on_close_callback=self._on_connection_closed)

    def publish_message(self, message, key=None) -> bool:
        """If the class is not stopping, publish a message to RabbitMQ,
        appending a list of deliveries with the message number that was sent.
        This list will be used to check for delivery confirmations in the
        on_delivery_confirmations method.

        Returns:
            bool: True if message successfully published to queue (channel was open and
                publish did not throw
                exception)
        """
        success = False
        if self._channel and self._channel.is_open:

            # We expect a JSON message format, do a check here...
            try:
                properties = pika.BasicProperties(content_type='application/json',
                                                  content_encoding='utf-8')

                self._channel.basic_publish(self._exchange.name, key,
                                            json.dumps(message, ensure_ascii=True),
                                            properties)
                self._records.message_number += 1
                self._records.deliveries[self._records.message_number] = message
                logger.debug('Published message # %i', self._records.message_number)
                success = True

            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error('Publish message problem : %s', str(e))
        return success

    def run(self):
        """Run the thread, i.e. get connection etc...
        """
        set_corr_id_context_var('PublishConfirm')

        self._connection = self.connect()
        self._connection.ioloop.start()

        while not self._stopping:
            time.sleep(5)

        if self._connection is not None and not self._connection.is_closed:
            # Finish closing
            self._connection.ioloop.start()

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
        self._close_channel()
        self._close_connection()

    def _on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        logger.debug('Connection opened')
        self._open_channel()

    def _on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        logger.error('Connection open failed, reopening in 5 seconds: %s', err)
        self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def _on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection _unused_connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        self._channel = None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: %s',
                           reason)
            self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def _open_channel(self):
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.
        """
        logger.debug('Creating a new channel')
        self._connection.channel(on_open_callback=self._on_channel_open)

    def _on_channel_open(self, channel: Channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        logger.debug('Channel opened')
        self._channel = channel
        self._add_on_channel_close_callback()
        self._setup_exchange(self._exchange)

    def _add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        logger.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self._on_channel_closed)

    def _on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        logger.warning('Channel %i was closed: %s', channel, reason)
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def _setup_exchange(self, exchange: Exch):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.
        :param str|unicode exchange_name: The name of the exchange to declare
        """
        logger.debug('Declaring exchange %s', exchange.name)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(self._on_exchange_declareok,
                               userdata=exchange.name)
        self._channel.exchange_declare(exchange=exchange.name,
                                       exchange_type=exchange.type,
                                       callback=cb)

    def _on_exchange_declareok(self, _unused_frame, userdata):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method _unused_frame: Exchange.DeclareOk response frame
        :param str|unicode userdata: Extra user data (exchange name)
        """
        logger.debug('Exchange declared: %s', userdata)
        self._setup_queue(self._queue)

    def _setup_queue(self, queue: Queue):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.
        :param str|unicode queue_name: The name of the queue to declare.
        """
        logger.debug('Declaring queue %s', queue.name)
        self._channel.queue_declare(queue=queue.name,
                                    durable=queue.durable,
                                    exclusive=queue.exclusive,
                                    auto_delete=queue.auto_delete,
                                    callback=self._on_queue_declareok)

    def _on_queue_declareok(self, _unused_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.
        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        """
        logger.debug('Binding %s to %s with %s', self._exchange.name, self._queue.name, '#')
        self._channel.queue_bind(self._queue.name,
                                 self._exchange.name,
                                 routing_key='#',  # Default wildcard key to consume everything
                                 callback=self._on_bindok)

    def _on_bindok(self, _unused_frame):
        """This method is invoked by pika when it receives the Queue.BindOk
        response from RabbitMQ. Since we know we're now setup and bound, it's
        time to start publishing."""
        logger.debug('Queue bound')
        self.start_publishing()

    def start_publishing(self):
        """This method will enable delivery confirmations and schedule the
        first message to be sent to RabbitMQ
        """
        logger.debug('Issuing consumer related RPC commands')
        self._enable_delivery_confirmations()
        # self.schedule_next_message()

    def _enable_delivery_confirmations(self):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.
        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.
        """
        logger.debug('Issuing Confirm.Select RPC command')
        if self._channel is not None:
            self._channel.confirm_delivery(self._on_delivery_confirmation)

    def _on_delivery_confirmation(self, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing housekeeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.
        :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame
        """
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        ack_multiple = method_frame.method.multiple
        delivery_tag = method_frame.method.delivery_tag

        logger.debug('Received %s for delivery tag: %i (multiple: %s)',
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

        # NOTE: at some point you would check self._deliveries for stale entries
        # and decide to attempt re-delivery
        logger.debug(
            'Published %i messages, %i have yet to be confirmed, '
            '%i were acked and %i were nacked', self._records.message_number,
            len(self._records.deliveries), self._records.acked, self._records.nacked)

    def _close_channel(self):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.
        """
        if self._channel is not None:
            logger.debug('Closing the channel')
            self._channel.close()

    def _close_connection(self):
        """This method closes the connection to RabbitMQ."""
        if self._connection is not None:
            logger.debug('Closing connection')
            self._connection.close()


def main():
    logging.config.dictConfig(get_default_log_config('INFO'))

    # Setup a test instance...
    conn = Conn('localhost', '/', '5672', 'guest', 'guest')
    exch = Exch('pub.conf.test', ExchangeType.topic)
    queue = Queue('pub.conf', '#', durable=False, exclusive=False, auto_delete=True)
    expub = PublishConfirm(conn, exch, queue)
    # Start the object thread, give it a moment...
    expub.start()
    time.sleep(1)

    while True:
        try:
            msg = input()
            key = 'publish.confirm.test'
            expub.publish_message(msg, key)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.info('Exiting from test loop : %s', str(e))
            break
    expub.stop()
    logger.info('Stopping...')


if __name__ == '__main__':
    main()
