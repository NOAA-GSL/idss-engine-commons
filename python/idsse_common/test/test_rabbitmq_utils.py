"""Testing for RabbitMqUtils functions"""
# ------------------------------------------------------------------------------
# Created on Wed Nov 8 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.  (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Mackenzie Grimes (2)
#
# ------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,missing-class-docstring,too-few-public-methods
# pylint: disable=redefined-outer-name,unused-argument,protected-access,duplicate-code,unused-import

import json
from typing import NamedTuple
from unittest.mock import MagicMock, Mock, patch, call
from uuid import UUID

from pytest import fixture, raises, MonkeyPatch
from pika import BasicProperties, BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

import idsse.common.rabbitmq_utils
from idsse.common.rabbitmq_utils import (
    Conn, Consumer, Exch, Queue, Publisher, RabbitMqParams, RabbitMqMessage,
    Rpc, subscribe_to_queue, _publish, _blocking_publish, _set_context
)

# Example data objects
CONN = Conn('localhost', '/', port=5672, username='user', password='password')
RMQ_PARAMS = RabbitMqParams(
    Exch('test_criteria_exch', 'topic'),
    Queue('test_criteria_queue', '', True, False, True)
)
EXAMPLE_UUID = 'b6591cc7-8b33-4cd3-aa22-408c83ac5e3c'


class Method(NamedTuple):
    """Mock of pika.frame.Method"""
    exchange: str = ' '
    queue: str = ''
    delivery_tag: int = 0
    routing_key: str = ''


class Frame(NamedTuple):
    """Mock of pika.frame.Frame"""
    method: Method


# fixtures
@fixture
def mock_channel() -> Mock:
    """Mock pika.adapters.blocking_connection.BlockingChannel object"""
    def mock_queue_declare(queue: str, **_kwargs) -> Method:
        return Frame(Method(queue=queue))  # create a usable (mock) Frame using queue name passed
    def mock_exch_declare(exchange: str, **_kwargs) -> Method:
        return Frame(Method(exchange=exchange))  # create a usable (mock) Frame using queue name passed

    mock_obj = Mock(spec=BlockingChannel, name='MockChannel')
    mock_obj.exchange_declare = Mock(side_effect=mock_exch_declare)
    mock_obj.queue_declare = Mock(side_effect=mock_queue_declare)
    mock_obj.is_open = True
    return mock_obj

@fixture
def mock_connection(mock_channel: Mock) -> Mock:
    """Mock pika.BlockingChannel object"""
    mock_obj = Mock(spec=BlockingConnection, name='MockConnection')
    mock_obj.channel = Mock(return_value=mock_channel)
    return mock_obj


@fixture
def mock_consumer(monkeypatch: MonkeyPatch, mock_connection: Mock, mock_channel: Mock) -> Mock:
    """Mock rabbitmq_utils.Consumer thread instance"""
    mock_obj = Mock(spec=Consumer, name='MockConsumer')
    mock_obj.return_value.is_alive = Mock(return_value=False)  # by default, thread not running
    mock_obj.return_value.connection = mock_connection
    mock_obj.return_value.channel = mock_channel
    # hack pika add_callback_threadsafe to invoke immediately (hides complexity of threading)
    mock_obj.return_value.channel.connection.add_callback_threadsafe = Mock(
        side_effect=lambda cb: cb()
    )

    monkeypatch.setattr('idsse.common.rabbitmq_utils.Consumer', mock_obj)
    return mock_obj

@fixture
def mock_publisher(monkeypatch: MonkeyPatch, mock_connection: Mock, mock_channel: Mock) -> Mock:
    """Mock rabbitmq_utils.Consumer thread instance"""
    mock_obj = Mock(spec=Publisher, name='MockPublisher')
    mock_obj.return_value.is_alive = Mock(return_value=False)  # by default, thread not running
    mock_obj.return_value.connection = mock_connection
    mock_obj.return_value.channel = mock_channel

    monkeypatch.setattr('idsse.common.rabbitmq_utils.Publisher', mock_obj)
    return mock_obj


@fixture
def mock_uuid(monkeypatch: MonkeyPatch) -> Mock:
    """Always return our example UUID str when UUID() is called"""
    mock_obj = Mock()
    mock_obj.UUID = Mock(side_effect=lambda: UUID(EXAMPLE_UUID))
    mock_obj.uuid4 = Mock(side_effect=lambda: EXAMPLE_UUID)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.uuid', mock_obj)
    return mock_obj


@fixture
def rpc_thread(mock_consumer: Mock, mock_uuid: Mock) -> Rpc:
    return Rpc(CONN, RMQ_PARAMS.exchange, timeout=5)


# tests
def test_connection_params_works(monkeypatch: MonkeyPatch, mock_connection: Mock):
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection)

    # run method
    mock_callback_function = Mock()
    _connection, _channel = subscribe_to_queue(CONN, RMQ_PARAMS, mock_callback_function)

    # assert correct (mocked) pika calls were made
    mock_blocking_connection.assert_called_once()
    _connection.channel.assert_called_once()  # pylint: disable=no-member

    _channel.basic_qos.assert_called_once()
    _channel.basic_consume.assert_called_once()

    # assert exchange was declared
    _channel.exchange_declare.assert_called_once_with(
        exchange=RMQ_PARAMS.exchange.name,
        exchange_type=RMQ_PARAMS.exchange.type,
        durable=RMQ_PARAMS.exchange.durable,
    )

    # assert queue was declared and bound
    _channel.queue_declare.assert_called_once_with(
        queue=RMQ_PARAMS.queue.name,
        exclusive=RMQ_PARAMS.queue.exclusive,
        durable=RMQ_PARAMS.queue.durable,
        auto_delete=RMQ_PARAMS.queue.auto_delete,
        arguments={}
    )

    _channel.queue_bind.assert_called_once_with(
        RMQ_PARAMS.queue.name,
        RMQ_PARAMS.exchange.name,
        RMQ_PARAMS.queue.route_key
    )

    # assert queue connected to message callback
    _channel.basic_consume.assert_called_once_with(
        queue=RMQ_PARAMS.queue.name,
        on_message_callback=mock_callback_function,
        auto_ack=False
    )


def test_private_queue_sets_ttl(monkeypatch: MonkeyPatch, mock_connection: Mock):
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection)
    example_queue = Queue('_my_private_queue', 'route_key', True, False, True)

    # run method
    mock_callback_function = Mock()
    _connection, _channel = subscribe_to_queue(
        CONN,
        RabbitMqParams(RMQ_PARAMS.exchange, example_queue),
        mock_callback_function)

    # assert correct (mocked) pika calls were made
    mock_blocking_connection.assert_called_once()
    _channel.basic_consume.assert_called_once()

    # assert queue was declared with message time-to-live of 10 seconds
    _channel.queue_declare.assert_called_once_with(
        queue=example_queue.name,
        exclusive=example_queue.exclusive,
        durable=example_queue.durable,
        auto_delete=example_queue.auto_delete,
        arguments={'x-message-ttl': 10000}
    )


def test_passing_connection_does_not_create_new(mock_connection: Mock, monkeypatch: MonkeyPatch):
    mock_callback_function = Mock(name='on_message_callback')
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection)

    new_connection, new_channel = subscribe_to_queue(CONN, RMQ_PARAMS, mock_callback_function)

    mock_connection.assert_not_called()
    assert new_connection == mock_connection
    # confirm that all channel setup proceeds normally
    new_channel.basic_consume.assert_called_once_with(
        queue=RMQ_PARAMS.queue.name,
        on_message_callback=mock_callback_function,
        auto_ack=False
    )


def test_passing_unsupported_connection_type_fails():
    with raises(ValueError) as exc:
        subscribe_to_queue('bad connection', RMQ_PARAMS, Mock(name='on_message_callback'))
    assert exc is not None


def test_direct_reply_does_not_declare_queue(monkeypatch: MonkeyPatch, mock_connection: Mock):
    params = RabbitMqParams(Exch('test_criteria_exch', 'topic'),
                            Queue('amq.rabbitmq.reply-to', '', True, False, True))

    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection)

    _, new_channel = subscribe_to_queue(CONN, params, Mock(name='mock_callback'))

    # assert that built-in Direct Reply-to queue was not recreated (pika would fail)
    new_channel.queue_declare.assert_not_called()
    new_channel.queue_bind.assert_not_called()
    new_channel.basic_consume.assert_called_once()


def test_default_exchange_does_not_declare_exchange(monkeypatch: MonkeyPatch,
                                                    mock_connection: Mock):
    params = RabbitMqParams(Exch('', 'topic'),
                            Queue('something', '', True, False, True))

    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection)

    _, new_channel = subscribe_to_queue(CONN, params, Mock())

    new_channel.exchange_declare.assert_not_called()
    new_channel.queue_declare.assert_called_once()
    new_channel.basic_consume.assert_called_once()


def test_simple_publisher(monkeypatch: MonkeyPatch, mock_connection: Mock):
    # add mock to get Connection callback to invoke immediately
    mock_connection.add_callback_threadsafe = Mock(side_effect=lambda callback: callback())
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection)

    mock_threadsafe = Mock()
    monkeypatch.setattr('idsse.common.rabbitmq_utils.threadsafe_call', mock_threadsafe)

    publisher = Publisher(CONN, RMQ_PARAMS.exchange)
    mock_blocking_connection.assert_called_once()
    _channel = mock_blocking_connection.return_value.channel
    _channel.assert_called_once()
    assert publisher.connection == mock_connection

    publisher.publish({'data': 123})
    assert 'Publisher.publish' in str(mock_threadsafe.call_args[0][1])

    publisher.stop()
    assert 'MockChannel.close' in str(mock_threadsafe.call_args[0][1])


def test_rpc_opens_new_connection_and_channel(rpc_thread: Rpc, mock_consumer: Mock):
    assert not rpc_thread.is_open
    rpc_thread.start()

    mock_consumer.return_value.start.assert_called_once()
    mock_consumer.return_value.is_alive = Mock(return_value=True)  # Consumer thread would be live

    # stop Rpc client and confirm that Consumer thread was closed
    rpc_thread.stop()
    mock_consumer.return_value.is_alive = Mock(return_value=False)  # Consumer thread would be dead

    assert not rpc_thread.is_open

    mock_consumer.return_value.stop.assert_called_once()
    mock_consumer.return_value.join.assert_called_once()


def test_stop_does_nothing_if_not_started(rpc_thread: Rpc, mock_consumer: Mock):
    # calling stop before starting does nothing
    rpc_thread.stop()
    mock_consumer.stop.assert_not_called()

    rpc_thread.start()
    mock_consumer.return_value.is_alive = Mock(return_value=True)  # Consumer thread would be live

    # calling start when already running does nothing
    mock_consumer.reset_mock()
    rpc_thread.start()
    mock_consumer.return_value.start.assert_not_called()


def test_send_request_works_without_calling_start(rpc_thread: Rpc,
                                                  mock_channel: Mock,
                                                  mock_connection: Mock,
                                                  mock_consumer: Mock,
                                                  monkeypatch: MonkeyPatch):
    example_message = {'value': 'hello world'}

    # when client calls _blocking_publish, manually invoke response callback with a faked message
    # from external service, simulating RMQ call/response
    # pylint: disable=too-many-arguments
    def mock_blocking_publish(*_args, **_kwargs):
        # build mock message from imaginary external service
        method = Method('', 123)
        props = BasicProperties(content_type='application/json', correlation_id=EXAMPLE_UUID)
        body = bytes(json.dumps(example_message), encoding='utf-8')

        rpc_thread._response_callback(mock_channel, method, props, body)

    monkeypatch.setattr('idsse.common.rabbitmq_utils._blocking_publish',
                        Mock(side_effect=mock_blocking_publish))

    result = rpc_thread.send_request(json.dumps({'fake': 'request message'}))
    assert json.loads(result.body) == example_message


def test_send_request_times_out_if_no_response(mock_connection: Mock,
                                               mock_consumer: Mock,
                                               mock_uuid: Mock,
                                               monkeypatch: MonkeyPatch):
    # create client with same parameters, except a very short timeout
    _thread = Rpc(CONN, RMQ_PARAMS.exchange, timeout=0.01)

    # do nothing on message publish
    monkeypatch.setattr('idsse.common.rabbitmq_utils._blocking_publish',
                        Mock(side_effect=lambda *_args, **_kwargs: None))

    result = _thread.send_request(json.dumps({'data': 123}))
    assert EXAMPLE_UUID not in _thread._pending_requests  # request was cleaned up
    assert result is None


def test_send_requests_returns_none_on_error(rpc_thread: Rpc,
                                             mock_connection: Mock,
                                             monkeypatch: MonkeyPatch):
    # pylint: disable=too-many-arguments
    def mock_blocking_publish(channel, exch, message_params, queue = None, success_flag = None,
                                done_event = None):
        # cause exception for pending request Future
        rpc_thread._pending_requests[EXAMPLE_UUID].set_exception(RuntimeError('Something broke'))

    monkeypatch.setattr('idsse.common.rabbitmq_utils._blocking_publish',
                        Mock(side_effect=mock_blocking_publish))

    result = rpc_thread.send_request({'data': 123})
    assert EXAMPLE_UUID not in rpc_thread._pending_requests  # request was cleaned up
    assert result is None

@fixture
def rabbitmq_conn_params():
    return Conn(host="localhost", v_host="/", port=5672, username="guest", password="guest")

def test_consumer_initialization(rabbitmq_conn_params, mock_connection, mock_channel):
    mock_callback = MagicMock()
    params_and_callbacks = [
        ((RMQ_PARAMS.exchange, RMQ_PARAMS.queue), mock_callback)
    ]

    consumer = Consumer(rabbitmq_conn_params, params_and_callbacks)

    # Assert connection and channel are created
    assert consumer.connection is not None
    assert consumer.channel is not None
    assert consumer._consumer_tags is not None


def test_consumer_stop(rabbitmq_conn_params, mock_connection, mock_channel):
    mock_callback = MagicMock()
    params_and_callbacks = [
        ((RMQ_PARAMS.exchange, RMQ_PARAMS.queue), mock_callback)
    ]

    consumer = Consumer(rabbitmq_conn_params, params_and_callbacks)
    consumer.stop()

def test_publisher_initialization(rabbitmq_conn_params, mock_channel):
    # pylint: disable=broad-exception-raised
    # Set exchange to mandatory and test for UUID added to exchange name
    exch = Exch('test_criteria_exch', 'topic', mandatory=True, delivery_conf=True)
    pub1 = Publisher(rabbitmq_conn_params, exch)

    # Assert connection and channel are created
    assert pub1.connection is not None
    assert pub1.channel is not None
    assert pub1._queue.name != exch.name
    if pub1.channel.confirm_delivery():
        raise Exception('confirm delivery not switched on!')

    pub2 = Publisher(rabbitmq_conn_params, RMQ_PARAMS.exchange)
    assert pub2.connection is not None
    assert pub2.channel is not None
    assert pub2._queue is None
    if pub1.channel.confirm_delivery():
        raise Exception('confirm delivery switched on!')
