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

from pytest import fixture, raises, MonkeyPatch

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

    Note that classes here are reduced functionality by far; only properties/methods/interfaces
    that exist here are the ones used by PublishConfirm (at the time tests were written)
    """
    def __init__(self):
        self.delivery_tag = 0  # pseudo-global to track messages we have "sent" to our mock server

    class Channel:
        """mock of pika.channel.Channel"""
        def __init__(self):
            self._context = MockPika()
            self.channel_number = 0
            self.is_open = True
            self.is_closed = False

        def __int__(self):
            """Return int representation of channel"""
            return self.channel_number

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

        def confirm_delivery(self, callback: Callable[[Method], None]):
            """
            Args:
                callback (Callable[[Method], None])
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
        def __init__(self,
                     parameters,
                     on_open_callback: Callable[[Any], None],
                     on_open_error_callback,
                     on_close_callback: Callable[[Any, str], None]):
            self.is_open = True
            self.is_closed = False
            self._context = MockPika()

            self.ioloop = self._context.IOLoop(on_open_callback, on_close_callback)

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
    """Create an instance of our mocked pika library. delivery_tag initialized to 0"""
    return MockPika()


@fixture
def publish_confirm(monkeypatch: MonkeyPatch, context: MockPika) -> PublishConfirm:
    monkeypatch.setattr('idsse.common.publish_confirm.SelectConnection', context.SelectConnection)
    return PublishConfirm(conn=EXAMPLE_CONN, exchange=EXAMPLE_EXCH, queue=EXAMPLE_QUEUE)


# tests
def test_publish_confirm_start_and_stop(publish_confirm: PublishConfirm):
    publish_confirm.start()

    assert publish_confirm._connection and publish_confirm._connection.is_open
    assert publish_confirm._channel and publish_confirm._channel.is_open
    assert publish_confirm._records.acked == 1  # channel.confirm_delivery() sent our first message

    publish_confirm.stop()

    assert publish_confirm._connection.is_closed
    assert publish_confirm._channel.is_closed


def test_delivery_confirmation_handles_nack(publish_confirm: PublishConfirm, context: MockPika):
    def mock_confirm_delivery(self: context.Channel, callback: Callable[[Method], None]):
        method = Method(Basic.Nack(delivery_tag=context.delivery_tag))
        self._context.delivery_tag += 1
        callback(method)

    publish_confirm._records.deliveries[0] = 'Confirm.Select'
    context.Channel.confirm_delivery = mock_confirm_delivery

    publish_confirm.start()
    assert publish_confirm._records.nacked == 1
    assert publish_confirm._records.acked == 0


def test_publish_message_success(publish_confirm: PublishConfirm):
    message_data = {'data': 123}

    publish_confirm.start()
    result = publish_confirm.publish_message(message_data)

    assert result
    assert publish_confirm._records.message_number == 1
    assert publish_confirm._records.deliveries[1] == message_data


def test_publish_message_exception_when_channel_not_open(publish_confirm: PublishConfirm):
    message_data = {'data': 123}

    # missing a publish_confirm.start(), should fail
    with raises(RuntimeError) as pytest_error:
        publish_confirm.publish_message(message_data)

    assert pytest_error is not None
    assert 'RabbitMQ channel is None' in str(pytest_error.value)
    assert publish_confirm._records.message_number == 0  # should not have logged message sent
    assert len(publish_confirm._records.deliveries) == 0


def test_publish_message_failure_rmq_error(publish_confirm: PublishConfirm):
    message_data = {'data': 123}

    publish_confirm.start()
    publish_confirm._channel.basic_publish = Mock(side_effect=RuntimeError('ACCESS_REFUSED'))
    success = publish_confirm.publish_message(message_data)

    # publish should have returned failure and not recorded a message delivery
    assert not success
    assert publish_confirm._records.message_number == 0
    assert len(publish_confirm._records.deliveries) == 0


def test_on_channel_closed(publish_confirm: PublishConfirm, context: MockPika):
    publish_confirm.start()
    publish_confirm._on_channel_closed(context.Channel(), 'ChannelClosedByClient')
    assert publish_confirm._channel is None
    assert publish_confirm._connection.is_closed


def test_start_with_callback(publish_confirm: PublishConfirm):
    example_message = {'callback_executed': True}

    def test_callback():
        assert publish_confirm._channel.is_open
        success = publish_confirm.publish_message(message=example_message)
        assert success

    assert publish_confirm._channel is None
    publish_confirm.start(callback=test_callback)

    sleep(.1)  # ensure that callback has time to run and send its message
    assert publish_confirm._records.message_number == 1
    assert publish_confirm._records.deliveries[1] == example_message


def test_start_without_callback_sleeps(publish_confirm: PublishConfirm, monkeypatch: MonkeyPatch):
    def mock_sleep_function(secs: float):
        # If this is not the call originating from PublishConfirm.start(), let it really sleep.
        # Mocking all sleep() calls seemed to break Thread operations (unit test ran forever)
        if secs != 0.2:
            sleep(secs)

    mock_sleep = Mock(wraps=mock_sleep_function)
    monkeypatch.setattr('idsse.common.publish_confirm.time.sleep', mock_sleep)

    # if no callback passed, start() should sleep internally to ensure RabbitMQ callbacks complete
    publish_confirm.start()

    # mock sleep someimtes captures a call from PublishConfirm.run(), due to a race condition
    # between this test's thread and the PublishConfirm thread. Both results are acceptable
    sleep_call_args = [call.args for call in mock_sleep.call_args_list]
    assert set(sleep_call_args) in [set([(0.2,)]), set([(0.2,), (5,)])]
