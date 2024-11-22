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
from pika.channel import Channel

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
        arguments={'x-message-ttl': 10000}
    )


def test_passing_connection_does_not_create_new(mock_connection, monkeypatch):
    mock_callback_function = Mock(name='on_message_callback')
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr(
        'idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection
    )

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


def test_simple_publisher_existing_channel(
    monkeypatch: MonkeyPatch, mock_connection: Mock, mock_channel: Mock
):
    mock_blocking_connection = Mock(return_value=mock_connection)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.BlockingConnection', mock_blocking_connection)
    mock_channel.__class__ = Channel  # make mock look like real pika.Channel

    publisher = Publisher(mock_channel, RMQ_PARAMS.exchange)

    mock_blocking_connection.assert_not_called()  # should not have created new Connection/Channel
    assert publisher.channel == mock_channel
    assert publisher.connection == mock_channel.connection

# TODO: copied unit tests from RiskProcessor RpcClient; can re-purpose but behavior a bit different
# import json
# from concurrent.futures import Future
# from time import sleep
# from typing import NamedTuple
# from unittest.mock import Mock
# from uuid import UUID

# from pytest import fixture, raises, MonkeyPatch
# from pika.adapters.blocking_connection import BlockingConnection, BlockingChannel
# from pika.spec import BasicProperties

# from idsse.common.rabbitmq_utils import Conn, Exch, Queue, RabbitMqParams
# from idsse.testing.utils.resources import get_resource_from_file

# from rabbitmq_utils import Rpc

# # Example data objects
# RPC_PARAMS = RpcClientParams(
#     conn=Conn('localhost', '/', port=5672, username='user', password='password'),
#     requests=RabbitMqParams(
#         Exch('data_exch', 'topic'),
#         Queue('data_request', '', True, False, True)
#     ),
#     responses=RabbitMqParams(
#         Exch('', 'topic'),
#         Queue('amq.rabbitmq.reply-to', '', True, False, True)
#     ),
#     timeout=5
# )
# EXAMPLE_UUID = 'b6591cc7-8b33-4cd3-aa22-408c83ac5e3c'

# # load test data from json files
# DATA_VALIDS_REQUEST: dict[str, any] = get_resource_from_file('idsse.testing.risk_processor',
#                                                              'data_service_valids_request.json')
# DATA_VALIDS_RESPONSE:dict[str, any] = get_resource_from_file('idsse.testing.risk_processor',
#                                                              'data_service_valids_response.json')

# class Method(NamedTuple):
#     """mock of pika.spec.Basic.Deliver Method"""
#     routing_key: str
#     delivery_tag: int


# # fixtures
# @fixture
# def mock_channel() -> Mock:
#     """Mock pika.adapters.blocking_connection.BlockingChannel object"""
#     mock_obj = Mock(spec=BlockingChannel, name='MockChannel')
#     mock_obj.basic_publish = Mock()
#     mock_obj.basic_ack = Mock()
#     mock_obj.basic_nack = Mock()
#     mock_obj.start_consuming = Mock()
#     mock_obj.stop_consuming = Mock()
#     mock_obj.close = Mock()
#     mock_obj.is_open = True
#     return mock_obj


# @fixture
# def mock_conn(mock_channel: Mock) -> Mock:
#     """Mock pika.BlockingChannel object"""
#     mock_obj = Mock(spec=BlockingConnection, name='MockConnection')
#     mock_obj.add_callback_threadsafe = Mock()
#     mock_obj.channel = Mock(return_value=mock_channel)
#     mock_obj.close = Mock()
#     mock_obj.process_data_events = Mock()
#     return mock_obj


# @fixture
# def mock_subscribe(monkeypatch: MonkeyPatch, mock_channel: Mock, mock_conn: Mock) -> Mock:
#     mock_function = Mock()
#     mock_function.return_value = (mock_conn, mock_channel)
#     monkeypatch.setattr('src.rpc_client.subscribe_to_queue', mock_function)
#     return mock_function


# @fixture
# def mock_uuid(monkeypatch: MonkeyPatch):
#     """Always return our example UUID str when UUID() is called"""
#     monkeypatch.setattr('src.rpc_client.uuid', Mock(side_effect=lambda: UUID(EXAMPLE_UUID)))


# @fixture
# def client(mock_subscribe: Mock, mock_uuid: Mock) -> RpcClient:
#     return RpcClient(RPC_PARAMS)


# # tests
# def test_start_opens_new_connection_and_channel(
#     client: RpcClient, mock_channel: Mock, mock_conn: Mock
# ):
#     assert not client.is_open
#     assert client._connection is None and client._channel is None

#     mock_conn.add_callback_threadsafe = Mock(side_effect=lambda callback: callback())
#     mock_channel.is_open = True
#     client.start()
#     sleep(0.1)  # ensure thread is started before verifying it updated private state variables

#     mock_channel.start_consuming.assert_called()
#     assert client.is_open
#     assert client._connection is not None
#     assert client._channel is not None and client._channel.is_open

#     # stop RpcClient and confirm that channel and connection were closed
#     client.stop()
#     mock_channel.is_open = False
#     assert not client._channel.is_open
#     assert not client.is_open

#     sleep(0.1)  # ensure thread has time to close private resources (asynchronously)
#     mock_channel.close.assert_called_once()
#     mock_conn.close.assert_called_once()


# def test_stop_does_nothing_if_not_started(client: RpcClient, mock_conn: Mock):
#     client.stop()
#     mock_conn.add_callback_threadsafe.assert_not_called()


# def test_starting_twice_does_nothing(client: RpcClient, mock_subscribe: Mock, mock_channel: Mock):
#     mock_channel.is_open = True
#     client.start()
#     # try:
#     client.start()
#     # except AssertionError:
#     #     fail('Thread should not be attempted to start twice')

#     sleep(0.1)  # ensure thread is started before verifying it made certain calls
#     mock_subscribe.assert_called_once()
#     mock_channel.start_consuming.assert_called_once()


# def test_send_request_works_without_calling_start(
#     client: RpcClient, mock_channel: Mock, mock_conn: Mock
# ):
#     # build mock message from data service
#     method = Method('', 123)
#     props = BasicProperties(
#         content_type='application/json',
#         correlation_id=EXAMPLE_UUID)
#     body = bytes(json.dumps(DATA_VALIDS_RESPONSE), encoding='utf-8')

#     # when client calls add_callback_threadsafe to publish message to data service, manually invoke
#     # response callback with a faked message from data service, simulating RMQ call/response
#     mock_conn.add_callback_threadsafe = Mock(side_effect=(
#         lambda _: client._response_callback(mock_channel, method, props, body)
#     ))

#     result = client.send_request(DATA_VALIDS_REQUEST)
#     assert result == DATA_VALIDS_RESPONSE


# def test_send_request_times_out_if_no_response(client: RpcClient, mock_conn: Mock):
#     # create client with same parameters, except a very short timeout
#     _client = RpcClient(RpcClientParams(
#         conn=RPC_PARAMS.conn,
#         requests=RPC_PARAMS.requests,
#         responses=RPC_PARAMS.responses,
#         timeout=0.01
#     ))
#     mock_conn.add_callback_threadsafe = Mock()  # do nothing on message publish

#     result = _client.send_request({'data': 123})
#     assert EXAMPLE_UUID in _client._pending_requests  # message was recorded
#     assert result is None


# def test_send_requests_returns_none_on_error(client: RpcClient, mock_conn: Mock):
#     mock_conn.add_callback_threadsafe = Mock(side_effect=(
#         lambda _: client._pending_requests[EXAMPLE_UUID].set_exception(
#             RuntimeError('Something broke')
#     )))

#     result = client.send_request({'data': 123})
#     assert EXAMPLE_UUID in client._pending_requests  # message was recorded
#     assert result is None


# def test_response_callback_sets_future_exc_on_bad_message(client: RpcClient, mock_channel: Mock):
#     # build mock message from data service
#     method = Method('', 123)
#     props = BasicProperties(content_type='text/html', correlation_id='abcd')
#     body = bytes('{"data": 123}', encoding='utf-8')

#     _future = Future()
#     client._pending_requests[props.correlation_id] = _future
#     client._response_callback(mock_channel, method, props, body)

#     assert _future.done
#     with raises(TypeError) as exc:
#         _future.result()

#     assert exc is not None and exc.type == TypeError
