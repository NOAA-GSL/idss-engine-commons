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
# pylint: disable=redefined-outer-name,unused-argument,protected-access,duplicate-code

from typing import NamedTuple
from unittest.mock import Mock

from pytest import fixture, raises, MonkeyPatch
from pika.adapters import blocking_connection

from idsse.common.rabbitmq_utils import (
    Conn, Exch, Queue, Publisher, RabbitMqParams, subscribe_to_queue
)

# Example data objects
CONN = Conn('localhost', '/', port=5672, username='user', password='password')
RMQ_PARAMS = RabbitMqParams(
    Exch('test_criteria_exch', 'topic'),
    Queue('test_criteria_queue', '', True, False, True)
)


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

    mock_obj = Mock(spec=blocking_connection.BlockingChannel, name='MockChannel')
    mock_obj.exchange_declare = Mock()
    mock_obj.queue_declare = Mock(side_effect=mock_queue_declare)
    mock_obj.queue_bind = Mock()
    mock_obj.basic_qos = Mock()
    mock_obj.close = Mock()

    return mock_obj


@fixture
def mock_connection(monkeypatch: MonkeyPatch, mock_channel: Mock) -> Mock:
    """Mock pika.BlockingChannel object"""
    mock_obj = Mock(name='MockConnection')
    mock_obj.channel = Mock(return_value=mock_channel)
    mock_obj.add_callback_threadsafe = Mock()
    mock_obj.close = Mock()

    return mock_obj


# tests
def test_connection_params_works(monkeypatch: MonkeyPatch, mock_connection: Mock):
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr(
        'idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection
    )

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
        arguments={'x-queue-type': 'classic'}
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
    monkeypatch.setattr(
        'idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection
    )
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
        arguments={'x-message-ttl': 10000, 'x-queue-type': 'classic'}
    )


def test_passing_connection_does_not_create_new(mock_connection, monkeypatch):
    mock_callback_function = Mock(name='on_message_callback')
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr(
        'idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection
    )

    new_connection, new_channel = subscribe_to_queue(
        CONN, RMQ_PARAMS, mock_callback_function
    )

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


def test_direct_reply_does_not_declare_queue(
    monkeypatch: MonkeyPatch, mock_connection: Mock
):
    params = RabbitMqParams(
        Exch('test_criteria_exch', 'topic'),
        Queue('amq.rabbitmq.reply-to', '', True, False, True)
    )

    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr(
        'idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection
    )

    _, new_channel = subscribe_to_queue(CONN, params, Mock(name='mock_callback'))

    # assert that built-in Direct Reply-to queue was not recreated (pika would fail)
    new_channel.queue_declare.assert_not_called()
    new_channel.queue_bind.assert_not_called()
    new_channel.basic_consume.assert_called_once()


def test_default_exchange_does_not_declare_exchange(
    monkeypatch: MonkeyPatch, mock_connection: Mock
):
    params = RabbitMqParams(
        Exch('', 'topic'),
        Queue('something', '', True, False, True)
    )

    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr(
        'idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection
    )

    _, new_channel = subscribe_to_queue(CONN, params, Mock())

    new_channel.exchange_declare.assert_not_called()
    new_channel.queue_declare.assert_called_once()
    new_channel.basic_consume.assert_called_once()


def test_simple_publisher(monkeypatch: MonkeyPatch, mock_connection: Mock):
    # add mock to get Connection callback to invoke immediately
    mock_connection.add_callback_threadsafe = Mock(side_effect=lambda callback: callback())
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr(
        'idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection
    )

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
