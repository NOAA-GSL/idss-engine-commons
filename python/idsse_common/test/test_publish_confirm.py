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
# pylint: disable=missing-class-docstring,too-few-public-methods,unnecessary-lambda,unused-argument

from time import sleep
from typing import Callable, Union, Self, Any
from unittest.mock import Mock

from pytest import fixture, MonkeyPatch

from pika.spec import Basic
from idsse.common.publish_confirm import PublishConfirm
from idsse.common.rabbitmq_utils import Conn, Exch, Queue

EXAMPLE_CONN = Conn('localhost', '/', 5672, 'guest', 'guest')
EXAMPLE_EXCH = Exch('pub.conf.test', 'topic')
EXAMPLE_QUEUE = Queue('pub.conf', '#', False, False, True)


class MockPika:
    """
    Mock classes to imitate pika functionality, callbacks, etc.
    Note that classes here are not full functionality; only properties/methods that
    PublishConfirm will try to invoke
    """
    delivery_tag = 0  # track how many messages we have "sent"

    class MethodFrame:
        def __init__(self, method):
            self.method = method

        @classmethod
        def create_method_frame(cls, method: Union[Basic.Ack, Basic.Nack]) -> Self:
            frame = cls(method(MockPika.delivery_tag))
            MockPika.delivery_tag += 1
            return frame


    class Channel:
        def __init__(self):
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
            """callback (Callable[[MockPika.MethodFrame], None])"""
            callback(EXAMPLE_ACK)

        def basic_publish(self, exchange: str, key: str, body: str, properties):
            MockPika.delivery_tag += 1


        def close(self):
            self.is_open = False
            self.is_closed = True


    class IOLoop:
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
        def __init__(self, parameters, on_open_callback, on_open_error_callback, on_close_callback):
            self.is_open = True
            self.is_closed = False

            self.ioloop = MockPika.IOLoop(on_open=on_open_callback, on_close=on_close_callback)

            self._on_open_callback = on_open_callback
            self._on_open_error_callback = on_open_error_callback
            self._on_close_callback = on_close_callback

        def channel(self, on_open_callback: Callable[[Any], None]):
            """on_open_callback (Callable[[MockPika.Channel], None])"""
            on_open_callback(MockPika.Channel())

        def close(self):
            self.is_open = False
            self.is_closed = True


# may need to make mockable in the future to pass Nack or customize delivery_tag
EXAMPLE_ACK = MockPika.MethodFrame.create_method_frame(Basic.Ack)


@fixture
def publish_confirm(monkeypatch: MonkeyPatch) -> PublishConfirm:
    monkeypatch.setattr('idsse.common.publish_confirm.SelectConnection', MockPika.SelectConnection)
    return PublishConfirm(conn=EXAMPLE_CONN, exchange=EXAMPLE_EXCH, queue=EXAMPLE_QUEUE)


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
    # sleep is here to keep our unit test (running on Main thread) from outrunning the external
    # PublishConfirm Thread. Not ideal, but using a callback makes test debugging very hard
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
    # sleep so our callback doesn't get outrun by this unit test
    sleep(.2)

    # delivery of imaginary message 0 should be gone now that message was "acked" by our test
    assert len(publish_confirm._records.deliveries) == 0
    mock_started_callback.assert_called_once()
