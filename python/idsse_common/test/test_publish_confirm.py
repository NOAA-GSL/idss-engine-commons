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

from collections.abc import Callable
from concurrent.futures import Future
from time import sleep
from typing import NamedTuple
from unittest.mock import Mock, PropertyMock

from pytest import fixture, raises, MonkeyPatch

from pika import SelectConnection
from pika.spec import Basic, Channel
from idsse.common.publish_confirm import PublishConfirm
from idsse.common.rabbitmq_utils import Conn, Exch, Queue

EXAMPLE_CONN = Conn('localhost', '/', 5672, 'guest', 'guest')
EXAMPLE_EXCH = Exch('pub.conf.test', 'topic')
EXAMPLE_QUEUE = Queue('pub.conf', '#', False, False, True)


class Method(NamedTuple):
    """mock of pika.frame.Method data class"""
    method: Basic.Ack | Basic.Nack


# fixtures
@fixture
def channel_state() -> dict:
    """
    Track the simulated state of our mock Channel, so it can be initialized with
    default values, read/written anywhere in a given test, and reset after each test finishes
    """
    return {
        'is_open': False,
        'delivery_tag': 0,  # track messages that have been mock "sent" over our channel
    }


@fixture
def mock_channel(channel_state: dict) -> Mock:
    # set up complex pytest Mock object to emulate Channel
    mock_obj = Mock(name='MockChannel', spec=Channel)
    channel = mock_obj.return_value
    channel.__int__= Mock(return_value=0)

    channel.is_open = PropertyMock(side_effect=lambda: channel_state['is_open'])
    channel.is_closed = PropertyMock(side_effect=lambda: not channel_state['is_open'])
    channel.exchange_declare.side_effect = (
        lambda exchange, exchange_type, callback: callback('userdata')
    )
    channel.queue_declare.side_effect = (
        lambda queue, durable, arguments, exclusive, auto_delete, callback: callback(None)
    )
    channel.queue_bind.side_effect = (
        lambda queue, exchange, routing_key, callback: callback(None)
    )

    def mock_confirm_delivery(callback):
        method = Method(Basic.Ack(channel_state['delivery_tag']))
        channel_state['delivery_tag'] += 1 # our Mock needs to track this message ID as "sent"
        callback(method)  # send new Ack message back to PublishConfirm
    channel.confirm_delivery.side_effect = mock_confirm_delivery

    def mock_basic_publish(exchange, key, body, properties):
        channel_state['delivery_tag'] += 1
    channel.basic_publish.side_effect = mock_basic_publish

    def mock_close():
        channel_state['is_open'] = False
    channel.close.side_effect = mock_close

    def mock_init(on_open_callback):
        channel_state['is_open'] = True
        on_open_callback(channel)
    mock_obj.side_effect = mock_init

    return mock_obj


@fixture
def conn_state() -> dict:
    """
    Track the simulated state of our mock Connection, so it can be initialized with
    default values, read/written anywhere in a given test, and reset after each test finishes
    """
    return {
        'is_open': False,
        # save Connection's open/close callbacks when Connection is initialized, to be invoked
        # when PublishConfirm.start/stop is called. These defaults should never run;
        # should be overwritten with real callbacks inside PublishConfirm._create_connection()
        'on_open': lambda: RuntimeError('on_open_callback not passed to SelectConnection()'),
        'on_close': lambda: RuntimeError('on_open_callback not passed to SelectConnection()'),
    }


@fixture
def mock_connection(monkeypatch: MonkeyPatch, mock_channel: Mock, conn_state: dict) -> Mock:
    mock_obj = Mock(name="MockConnection", spec=SelectConnection)

    connection = mock_obj.return_value
    connection.is_open = PropertyMock(side_effect=lambda: conn_state['is_open'])
    connection.channel = mock_channel

    # pylint: disable=unnecessary-lambda
    connection.ioloop.start.side_effect = lambda: conn_state['on_open']()
    connection.ioloop.stop.side_effect = lambda: conn_state['on_close']()

    def mock_close():
        conn_state['is_open'] = False
    connection.close.side_effect = mock_close

    def mock_init(parameters, on_open_callback, on_open_error_callback, on_close_callback):
        conn_state['is_open'] = True
        conn_state['on_open'] = lambda: on_open_callback(connection)
        conn_state['on_close'] = lambda: on_close_callback(connection, 'Closed by test')

        return connection
    mock_obj.side_effect = mock_init

    monkeypatch.setattr('idsse.common.publish_confirm.SelectConnection', mock_obj)
    return mock_obj


@fixture
def publish_confirm(mock_connection: Mock) -> PublishConfirm:
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


def test_delivery_confirmation_handles_nack(
    publish_confirm: PublishConfirm, mock_connection: Mock, channel_state: dict
):
    def mock_confirm_delivery(callback: Callable[[Method], None]):
        method = Method(Basic.Nack(channel_state['delivery_tag']))
        channel_state['delivery_tag'] += 1
        callback(method)

    publish_confirm._records.deliveries[0] = 'Confirm.Select'
    mock_connection.return_value.channel.return_value.confirm_delivery = mock_confirm_delivery

    publish_confirm.start()
    assert publish_confirm._records.nacked == 1
    assert publish_confirm._records.acked == 0


def test_wait_for_channel_to_be_ready_timeout(publish_confirm: PublishConfirm):
    # start() doesn't call its callback in time (at all), so timeout should expire
    publish_confirm.start = Mock(side_effect=lambda is_ready: None)

    # run wait_for_channel which should timeout waiting for Future to resolve
    channel_is_ready = publish_confirm._wait_for_channel_to_be_ready(timeout=0.3)
    assert not channel_is_ready
    publish_confirm.start.assert_called_once()

    # teardown by undoing our hacky mock
    publish_confirm.start = PublishConfirm.start


def test_publish_message_success_without_calling_start(mock_connection: Mock):
    pub_conf = PublishConfirm(conn=EXAMPLE_CONN, exchange=EXAMPLE_EXCH, queue=EXAMPLE_QUEUE)
    example_message = {'data': [123]}

    assert pub_conf._connection is None and pub_conf._channel is None
    success = pub_conf.publish_message(example_message)

    # connection & channel should have been initialized internally, so publish should have worked
    assert success
    assert pub_conf._channel is not None and pub_conf._channel.is_open
    assert pub_conf._records.message_number == 1
    assert pub_conf._records.deliveries[1] == example_message


def test_publish_message_failure_rmq_error(publish_confirm: PublishConfirm, mock_connection: Mock):
    message_data = {'data': 123}
    mock_connection.return_value.channel.return_value.basic_publish = Mock(
        side_effect=[RuntimeError('ACCESS_REFUSED'), RuntimeError('ACCESS_REFUSED')]
    )

    # return immediately without doing any Thread starting
    # we do this to simplify test results, because multithreading muddies the waters for mocks
    def mock_start(is_ready: Future | None = None):
        if is_ready is not None:
            is_ready.set_result(True)
    publish_confirm.start = mock_start

    success = publish_confirm.publish_message(message_data)

    # publish should have returned failure and not recorded a message delivery
    assert not success
    assert publish_confirm._records.message_number == 0
    assert len(publish_confirm._records.deliveries) == 0

    # teardown our ad-hoc mocking of PublishConfirm instance
    publish_confirm.start = PublishConfirm.start
    publish_confirm.stop()


def test_publish_failure_restarts_thread(publish_confirm: PublishConfirm, mock_connection: Mock):
    message_data = {'data': 123}

    # fail the first publish, succeed without incident on the second
    mock_connection.return_value.channel.return_value.basic_publish = Mock(
        side_effect=[RuntimeError('ACCESS_REFUSED'), None]
    )

    initial_thread_name = publish_confirm._thread.name
    success = publish_confirm.publish_message(message_data)  # TODO: raises RuntimeError, but why??
    assert success
    assert publish_confirm._thread.name != initial_thread_name  # should have new Thread


def test_on_channel_closed(publish_confirm: PublishConfirm, mock_connection: Mock):
    publish_confirm.start()
    assert publish_confirm._channel.is_open

    channel = mock_connection.return_value.channel.return_value
    publish_confirm._on_channel_closed(channel, 'ChannelClosedByClient')

    assert publish_confirm._channel is None
    assert publish_confirm._connection.is_closed

    publish_confirm.stop()  # teardown


def test_start_with_future(publish_confirm: PublishConfirm):
    is_channel_ready = Future()
    assert publish_confirm._channel is None

    # run test
    publish_confirm.start(is_channel_ready)
    assert is_channel_ready.result(timeout=2)

    # teardown
    publish_confirm.stop()


def test_exchange_failure_raises_exception(monkeypatch: MonkeyPatch, mock_connection: Mock):
    # set up mock Channel that will fail on RabbitMQ exchange declare step
    mock_connection.return_value.channel.return_value.exchange_declare = Mock(
        side_effect=ValueError('Precondition failed: exchange did not match')
    )

    pub_conf = PublishConfirm(conn=EXAMPLE_CONN, exchange=EXAMPLE_EXCH, queue=EXAMPLE_QUEUE)

    # run test
    is_channel_ready = Future()
    pub_conf.start(is_ready=is_channel_ready)
    exc = is_channel_ready.exception()
    assert isinstance(exc, ValueError) and 'Precondition failed' in str(exc.args[0])


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
    assert set(sleep_call_args) in [set([(0.2,)]), set([(0.2,), (0.1,)])]


def test_wait_for_channel_returns_when_ready(publish_confirm: PublishConfirm):
    publish_confirm._connection = None
    publish_confirm._channel = None

    is_ready = publish_confirm._wait_for_channel_to_be_ready()
    assert is_ready
    assert publish_confirm._channel is not None and publish_confirm._channel.is_open


def test_calling_start_twice_raises_error(mock_connection: Mock):
    pub_conf = PublishConfirm(conn=EXAMPLE_CONN, exchange=EXAMPLE_EXCH, queue=EXAMPLE_QUEUE)

    pub_conf.start()
    with raises(RuntimeError) as exc:
        pub_conf.start()
    assert exc is not None
