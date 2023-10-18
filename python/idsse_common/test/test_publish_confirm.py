"""Test suite for publish_confirm.py"""
# ----------------------------------------------------------------------------------
# Created on Wed Oct 18 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#    Mackenzie Grimes (2)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name,protected-access
# pylint: disable=too-few-public-methods,unused-argument

from time import sleep
from typing import Callable, Union, Any, NamedTuple
from unittest.mock import Mock

from pytest import fixture, MonkeyPatch

from pika.spec import Basic
from idsse.common.publish_confirm import PublishConfirm
from idsse.common.rabbitmq_utils import Conn, Exch, Queue

EXAMPLE_CONN = Conn('localhost', '/', 5672, 'guest', 'guest')
EXAMPLE_EXCH = Exch('pub.conf.test', 'topic')
EXAMPLE_QUEUE = Queue('pub.conf', '#', False, False, True)


class Method(NamedTuple):
    """mock of pika.frame.Method data class"""
    method: Union[Basic.Ack, Basic.Nack]


class MockPika:
    """
    Mock classes to imitate pika functionality, callbacks, etc.

    Note that classes here are by far reduced functionality; only properties/methods/interfaces
    that PublishConfirm uses (when this unit test was written)
    """
    def __init__(self):
        self.delivery_tag = 0  # pseudo-global to track messages we have "sent" to our mock server

    class Channel:
        """mock of pika.channel.Channel"""
        def __init__(self):
            self._context = MockPika()
            self.is_open = True
            self.is_closed = False

        def add_on_close_callback(self, callback):
            pass

        def exchange_declare(self, exchange, exchange_type, callback: Callable[[Any, str], None]):
            callback('userdata')

        # pylint: disable=too-many-arguments
        def queue_declare(
            self, queue, durable, exclusive, auto_delete, callback: Callable[[Any], None]
        ):
            callback(None)

        def queue_bind(self, queue, exchange, routing_key, callback: Callable[[Any], None]):
            callback(None)  # connection expected, but PublishConfirm doesn't actually use it

        def confirm_delivery(self, callback: Callable[[Any], None]):
            """
            Args:
                callback (Callable[[MockPika.MethodFrame], None])
            """
            # may need to make this mockable in the future to pass Nack or customize delivery_tag
            method = Method(Basic.Ack(delivery_tag=self._context.delivery_tag))
            self._context.delivery_tag += 1  # MockPika needs to track this message ID as "sent"

            callback(method)  # send new Ack message back to PublishConfirm

        def basic_publish(self, exchange: str, key: str, body: str, properties):
            self._context.delivery_tag += 1

        def close(self):
            self.is_open = False
            self.is_closed = True


    class IOLoop:
        """mock of pika.SelectConnection.ioloop"""
        def __init__(self, on_open: Callable[[Any], None], on_close: Callable[[Any, str], None]):
            self.on_open = on_open
            self.on_close = on_close

        def start(self):
            self.on_open(None)

        def stop(self):
            self.on_close(None, 'some_reason')

        def call_later(self):
            pass


    class SelectConnection:
        """mock of pika.SelectConnection"""
        def __init__(self, parameters, on_open_callback, on_open_error_callback, on_close_callback):
            self.is_open = True
            self.is_closed = False
            self._context = MockPika()

            self.ioloop = self._context.IOLoop(
                on_open=on_open_callback, on_close=on_close_callback
            )

            self._on_open_callback = on_open_callback
            self._on_open_error_callback = on_open_error_callback
            self._on_close_callback = on_close_callback

        def channel(self, on_open_callback: Callable[[Any], None]):
            """
            Args:
                on_open_callback (Callable[[MockPika.Channel], None])
            """
            on_open_callback(self._context.Channel())

        def close(self):
            self.is_open = False
            self.is_closed = True


# fixtures
@fixture
def context() -> MockPika:
    """Create instance of our mocked pika library"""
    return MockPika()


@fixture
def publish_confirm(monkeypatch: MonkeyPatch, context: MockPika) -> PublishConfirm:
    monkeypatch.setattr('idsse.common.publish_confirm.SelectConnection', context.SelectConnection)
    return PublishConfirm(conn=EXAMPLE_CONN, exchange=EXAMPLE_EXCH, queue=EXAMPLE_QUEUE)


# tests
def test_publish_confirm_start_and_stop(publish_confirm: PublishConfirm):
    publish_confirm.start()
    sleep(.2)

    assert publish_confirm._connection and publish_confirm._connection.is_open
    assert publish_confirm._channel and publish_confirm._channel.is_open

    publish_confirm.stop()
    sleep(.2)

    assert publish_confirm._connection.is_closed
    assert publish_confirm._channel.is_closed


def test_publish_message(publish_confirm: PublishConfirm):
    message_data = {'data': 123}

    previous_message_number = publish_confirm._records.message_number
    publish_confirm.start()
    # sleep here to keep our unit test (Main thread) from outrunning the PublishConfirm Thread.
    # Not ideal, but using a callback made debugging very hard (breakpoints don't stop all threads)
    sleep(.2)

    result = publish_confirm.publish_message(message_data)

    assert result
    current_message_number = publish_confirm._records.message_number
    assert current_message_number > previous_message_number
    assert publish_confirm._records.deliveries[current_message_number] == message_data


def test_publish_confirm_start_with_callback(publish_confirm: PublishConfirm):
    mock_started_callback = Mock()
    publish_confirm._records.deliveries[0] = 'Confirm.Select'

    publish_confirm.start(callback=mock_started_callback)
    # sleep so our callback doesn't get outrun by this unit test.
    # Less confusing to read than creating a real callback function and putting asserts there
    sleep(.2)

    # delivery of imaginary message 0 should be gone now that message was "acked" by our test
    assert len(publish_confirm._records.deliveries) == 0
    mock_started_callback.assert_called_once()
