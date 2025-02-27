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
# pylint: disable=redefined-outer-name,unused-argument,duplicate-code,protected-access
import json
from threading import Event
from typing import NamedTuple
from unittest.mock import MagicMock, Mock, patch, ANY
from uuid import UUID

from pytest import fixture, raises, MonkeyPatch
from pika import BasicProperties, BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import UnroutableError

from idsse.common.rabbitmq_utils import (
    DIRECT_REPLY_QUEUE, Conn, Consumer, Exch, Future, Queue, Publisher, RabbitMqParams,
    RabbitMqParamsAndCallback, RabbitMqMessage, RpcConsumer, RpcPublisher, RpcResponse,
    subscribe_to_queue, _publish, _setup_exch_and_queue, threadsafe_call, threadsafe_ack,
    threadsafe_nack
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
        return Frame(Method(exchange=exchange))

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
def mock_uuid(monkeypatch: MonkeyPatch) -> Mock:
    """Always return our example UUID str when UUID() is called"""
    mock_obj = Mock()
    mock_obj.UUID = Mock(side_effect=lambda: UUID(EXAMPLE_UUID))
    mock_obj.uuid4 = Mock(side_effect=lambda: EXAMPLE_UUID)
    monkeypatch.setattr('idsse.common.rabbitmq_utils.uuid', mock_obj)
    return mock_obj


@fixture
def rpc_thread(mock_consumer: Mock, mock_uuid: Mock) -> RpcPublisher:
    return RpcPublisher(CONN, RMQ_PARAMS.exchange, timeout=5)


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


def test_rpc_opens_new_connection_and_channel(rpc_thread: RpcPublisher, mock_consumer: Mock):
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


def test_stop_does_nothing_if_not_started(rpc_thread: RpcPublisher, mock_consumer: Mock):
    # calling stop before starting does nothing
    rpc_thread.stop()
    mock_consumer.stop.assert_not_called()

    rpc_thread.start()
    mock_consumer.return_value.is_alive = Mock(return_value=True)  # Consumer thread would be live

    # calling start when already running does nothing
    mock_consumer.reset_mock()
    rpc_thread.start()
    mock_consumer.return_value.start.assert_not_called()


def test_send_request_works_without_calling_start(rpc_thread: RpcPublisher,
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
        props = BasicProperties(content_type='application/json', headers={'rpc': EXAMPLE_UUID})
        body = bytes(json.dumps(example_message), encoding='utf-8')
        rpc_thread._on_response(mock_channel, method, props, body)

    monkeypatch.setattr('idsse.common.rabbitmq_utils._blocking_publish',
                        Mock(side_effect=mock_blocking_publish))

    result = rpc_thread.send_request(RabbitMqMessage(json.dumps({'fake': 'request message'})))
    assert json.loads(result.body) == example_message


def test_send_request_times_out_if_no_response(mock_connection: Mock,
                                               mock_consumer: Mock,
                                               mock_uuid: Mock,
                                               monkeypatch: MonkeyPatch):
    # create client with same parameters, except a very short timeout
    _thread = RpcPublisher(CONN, RMQ_PARAMS.exchange, timeout=0.01)

    # do nothing on message publish
    monkeypatch.setattr('idsse.common.rabbitmq_utils._blocking_publish',
                        Mock(side_effect=lambda *_args, **_kwargs: None))

    result = _thread.send_request(RabbitMqMessage(json.dumps({'data': 123})))
    assert EXAMPLE_UUID not in _thread._pending_requests  # request was cleaned up
    assert result is None


def test_send_requests_returns_none_on_error(rpc_thread: RpcPublisher, mock_channel: Mock):
    # pylint: disable=too-many-arguments
    def mock_basic_publish(exchange, routing_key, body, properties = None, mandatory = False):
        # cause exception for pending request Future
        rpc_thread._pending_requests[EXAMPLE_UUID].set_exception(RuntimeError('Something broke'))
    mock_channel.basic_publish.side_effect = mock_basic_publish

    result = rpc_thread.send_request(RabbitMqMessage({'data': 123}))

    assert EXAMPLE_UUID not in rpc_thread._pending_requests  # request was cleaned up
    assert result is None


def test_nacks_unrecognized_response(rpc_thread: RpcPublisher,
                                     mock_connection: Mock,
                                     mock_channel: Mock,
                                     monkeypatch: MonkeyPatch):
    rpc_thread._pending_requests = {'abcd': Future()}
    delivery_tag = 123
    props = BasicProperties(content_type='application/json', headers={'rpc': 'unknown_id'})
    body = bytes(json.dumps({'data': 123}), encoding='utf-8')

    rpc_thread._on_response(mock_channel, Method(delivery_tag=delivery_tag), props, body)

    # unregistered message was nacked
    mock_channel.basic_nack.assert_called_with(delivery_tag=delivery_tag, requeue=False)
    # pending requests inside Rpc was not touched
    assert 'abcd' in rpc_thread._pending_requests
    assert not rpc_thread._pending_requests['abcd'].done()


def test_send_request_preserves_props(rpc_thread: RpcPublisher, mock_channel: Mock):
    # pylint: disable=too-many-arguments
    def mock_basic_publish(exchange, routing_key, body, properties = None, mandatory = False):
        # cause exception for pending request Future
        rpc_thread._pending_requests[EXAMPLE_UUID].set_exception(RuntimeError('Something broke'))
    mock_channel.basic_publish.side_effect = mock_basic_publish

    result = rpc_thread.send_request(RabbitMqMessage({'data': 123}))

    assert EXAMPLE_UUID not in rpc_thread._pending_requests  # request was cleaned up
    assert result is None


def test_rpc_consumer_start_stop(mock_consumer: Mock):
    mock_consumer.return_value.is_alive.return_value = False
    rpc_consumer = RpcConsumer(CONN, RMQ_PARAMS, lambda: None)

    rpc_consumer.start()
    mock_consumer.return_value.start.assert_called_once()

    mock_consumer.return_value.is_alive.return_value = True

    rpc_consumer.stop()
    mock_consumer.return_value.stop.assert_called_once()


def test_rpc_consumer_on_message_ack(mock_channel: Mock, mock_consumer: Mock):
    example_response = RabbitMqMessage('{"response": "bar"}',
                                       BasicProperties(content_type='application/json',
                                                       correlation_id='some-correlation-id'))
    mock_on_request = Mock(return_value=RpcResponse(example_response, ack=True))
    inbound_tag = 7
    inbound_rpc_id = '123'
    inbound_reply_to = f'{DIRECT_REPLY_QUEUE}.g1h2AA5yZXBseUA1NTQ3NDU0OQAWaZUAAAAAZ7FK9g=='
    inbound_props = BasicProperties(content_type='text/html',
                                    headers={'rpc': inbound_rpc_id},
                                    reply_to=inbound_reply_to)
    inbound_body = bytes('{"request": "foo"}', encoding='utf-8')
    rpc_consumer = RpcConsumer(CONN, RMQ_PARAMS, mock_on_request)

    rpc_consumer._on_message(mock_channel, Method('', '', inbound_tag), inbound_props, inbound_body)

    mock_channel.basic_ack.assert_called_once_with(inbound_tag)
    assert mock_channel.basic_publish.call_count == 1
    published_args = mock_channel.basic_publish.call_args[1]
    assert published_args['body'] == example_response.body
    assert published_args['properties'].reply_to == inbound_reply_to
    assert published_args['properties'].content_type == 'application/json'
    assert published_args['properties'].correlation_id == 'some-correlation-id'
    assert published_args['properties'].headers['rpc'] == inbound_rpc_id


def test_rpc_consumer_on_message_nack(mock_channel: Mock, mock_consumer: Mock):
    example_response = RabbitMqMessage('{"response": "bar"}',
                                       BasicProperties(content_type='application/json'))
    mock_on_request = Mock(return_value=RpcResponse(example_response, ack=False, requeue=True))
    inbound_tag = 7
    inbound_props = BasicProperties(content_type='application/json',
                                    headers={'rpc': '123'},
                                    reply_to=DIRECT_REPLY_QUEUE)
    inbound_body = bytes('{"request": "foo"}', encoding='utf-8')
    rpc_consumer = RpcConsumer(CONN, RMQ_PARAMS, mock_on_request)

    rpc_consumer._on_message(mock_channel, Method('', '', inbound_tag), inbound_props, inbound_body)

    mock_channel.basic_nack.assert_called_once_with(inbound_tag, requeue=True)


@fixture
def mock_conn_params():
    return Conn(
        host='localhost',
        v_host='/',
        port=5672,
        username='guest',
        password='guest'
    )


@fixture
def mock_rmq_params_and_callback():
    exchange = Exch(name="test_exchange", type="direct")
    queue = Queue(name="test_queue",
                  route_key="test_key",
                  durable=True,
                  exclusive=False,
                  auto_delete=False)
    params = RabbitMqParams(exchange=exchange, queue=queue)
    callback = MagicMock()
    return RabbitMqParamsAndCallback(params=params, callback=callback)


@patch('idsse.common.rabbitmq_utils.BlockingConnection')
@patch('idsse.common.rabbitmq_utils.ThreadPoolExecutor')
def test_consumer_initialization(mock_executor, mock_blocking_connection, mock_conn_params,
                                 mock_rmq_params_and_callback, mock_channel):
    mock_blocking_connection.return_value.channel.return_value = mock_channel
    Consumer(conn_params=mock_conn_params, rmq_params_and_callbacks=mock_rmq_params_and_callback)
    mock_blocking_connection.assert_called_once_with(mock_conn_params.connection_parameters)
    mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)


@patch('idsse.common.rabbitmq_utils.BlockingConnection')
@patch('idsse.common.rabbitmq_utils.ThreadPoolExecutor')
def test_consumer_start(mock_executor, mock_blocking_connection, mock_conn_params,
                        mock_rmq_params_and_callback, mock_channel):
    mock_blocking_connection.return_value.channel.return_value = mock_channel
    consumer = Consumer(conn_params=mock_conn_params,
                        rmq_params_and_callbacks=mock_rmq_params_and_callback)
    with patch.object(consumer.channel, 'start_consuming') as start_consuming:
        consumer.run()
        start_consuming.assert_called_once()


@patch('idsse.common.rabbitmq_utils.BlockingConnection')
@patch('idsse.common.rabbitmq_utils.ThreadPoolExecutor')
def test_on_message(mock_executor, mock_blocking_connection, mock_conn_params,
                    mock_rmq_params_and_callback, mock_channel):
    mock_blocking_connection.return_value.channel.return_value = mock_channel
    consumer = Consumer(conn_params=mock_conn_params,
                        rmq_params_and_callbacks=mock_rmq_params_and_callback)
    mock_func = MagicMock()
    consumer._on_message(mock_channel, MagicMock(), MagicMock(), b"Test Message", func=mock_func)
    mock_executor.return_value.submit.assert_called_once_with(consumer.context.run,
                                                              mock_func,
                                                              mock_channel,
                                                              ANY,
                                                              ANY,
                                                              b"Test Message")


@fixture
def mock_message():
    return MagicMock(name='RabbitMqMessage', spec=dict)


@fixture
def mock_queue():
    return MagicMock(name='Queue', spec=dict)


def test_publish_success(mock_channel, mock_queue):
    # Arrange
    exch = Exch(name='test', type='topic', mandatory=True)
    RabbitMqMessage.route_key = None
    success_flag = [False]
    done_event = Event()

    # Act
    _publish(
        mock_channel,
        exch,
        RabbitMqMessage,
        queue=mock_queue,
        success_flag=success_flag,
        done_event=done_event,
    )

    # Assert
    mock_channel.basic_publish.assert_called_once_with(
        exch.name,
        RabbitMqMessage.route_key or exch.route_key,
        body=RabbitMqMessage.body,
        properties=RabbitMqMessage.properties,
        mandatory=exch.mandatory,
    )
    assert success_flag[0] is True
    assert done_event.is_set()


def test_publish_failure(mock_channel):
    # Arrange
    mock_channel.basic_publish.side_effect = Exception("Publish error")
    success_flag = [False]
    done_event = Event()
    exch = Exch(name='test', type='topic', route_key='test.route', mandatory=True)

    # Act & Assert
    with raises(Exception, match="Publish error"):
        _publish(
            mock_channel,
            exch,
            RabbitMqMessage,
            success_flag=success_flag,
            done_event=done_event,
        )

    assert success_flag[0] is False
    assert done_event.is_set()


def test_publish_with_private_queue(mock_channel, mock_queue):
    # Arrange
    mock_queue.name = "_private_queue"
    mock_queue.auto_delete = True
    success_flag = [False]
    done_event = Event()
    exch = Exch(name='test', type='topic', route_key='test.route', mandatory=False)
    msg = RabbitMqMessage(body={'data': 123}, route_key='', properties=None)

    # Act
    _publish(
        mock_channel,
        exch,
        msg,
        queue=mock_queue,
        success_flag=success_flag,
        done_event=done_event,
    )

    # Assert
    assert success_flag[0] is True
    assert done_event.is_set()


def test_publish_unroutable_error(mock_channel, mock_message):
    # Arrange
    mock_channel.basic_publish.side_effect = UnroutableError(mock_message)
    success_flag = [False]
    done_event = Event()
    exch = Exch(name='test', type='topic', route_key='test.route')
    msg = RabbitMqMessage(body={'data': 123}, route_key='', properties=None)

    # Act
    _publish(
        mock_channel,
        exch,
        msg,
        success_flag=success_flag,
        done_event=done_event,
    )

    # Assert
    assert success_flag[0] is False
    assert done_event.is_set()


def test_setup_exch_and_queue_with_default_exchange(mock_channel):
    """Test setup when using the default exchange (no exchange declaration or binding)."""
    exch = Exch(name="", type="direct")
    queue = Queue(name="test_queue",
                  route_key="test_key",
                  durable=True,
                  exclusive=False,
                  auto_delete=False)

    _setup_exch_and_queue(mock_channel, exch, queue)
    mock_channel.queue_bind.assert_not_called()


def test_setup_exch_and_queue_with_exchange(mock_channel):
    """Test setup with a named exchange and binding to a queue."""
    exch = Exch(name="test_exchange", type="direct")
    queue = Queue(name="test_queue",
                  route_key="test_key",
                  durable=True,
                  exclusive=False,
                  auto_delete=False)

    with patch('idsse.common.rabbitmq_utils._setup_exch') as mock_setup_exch:
        _setup_exch_and_queue(mock_channel, exch, queue)

        mock_setup_exch.assert_called_once_with(mock_channel, exch)
        mock_channel.queue_bind.assert_called_once_with(
            "test_queue",
            exchange="test_exchange",
            routing_key="test_key"
        )


def test_setup_exch_and_queue_with_quorum_queue(mock_channel):
    """Test that ValueError is raised for quorum queues with auto_delete=True."""
    exch = Exch(name="test_exchange", type="direct")
    queue = Queue(
        name="test_queue",
        route_key="test_key",
        durable=True,
        exclusive=False,
        auto_delete=True,
        arguments={"x-queue-type": "quorum"}
    )

    with raises(ValueError, match="Quorum queues can not be configured to auto delete"):
        _setup_exch_and_queue(mock_channel, exch, queue)


def test_setup_exch_and_queue_direct_reply_to(mock_channel):
    """Test behavior with the Direct Reply-to queue."""
    exch = Exch(name="", type="direct")
    queue = Queue(name="amq.rabbitmq.reply-to",
                  route_key="test_key",
                  durable=False,
                  exclusive=True,
                  auto_delete=False)

    _setup_exch_and_queue(mock_channel, exch, queue)

    mock_channel.queue_declare.assert_not_called()
    mock_channel.queue_bind.assert_not_called()


def test_threadsafe_call_with_open_channel(mock_channel):
    """Test threadsafe_call when the channel is open."""
    mock_func1 = MagicMock()
    mock_func2 = MagicMock()
    threadsafe_call(mock_channel, mock_func1, mock_func2)

    assert mock_channel.connection.add_callback_threadsafe.called
    callback = mock_channel.connection.add_callback_threadsafe.call_args[0][0]
    callback()

    mock_func1.assert_called_once()
    mock_func2.assert_called_once()


def test_threadsafe_call_with_closed_channel(mock_channel):
    """Test threadsafe_call when the channel is closed."""
    mock_channel.is_open = False
    mock_func = MagicMock()

    threadsafe_call(mock_channel, mock_func)

    assert mock_channel.connection.add_callback_threadsafe.called
    callback = mock_channel.connection.add_callback_threadsafe.call_args[0][0]
    with raises(ConnectionError):
        callback()
    mock_func.assert_not_called()


def test_threadsafe_ack(mock_channel):
    """Test threadsafe_ack functionality."""
    delivery_tag = 123
    mock_extra_func = MagicMock()

    threadsafe_ack(mock_channel, delivery_tag, extra_func=mock_extra_func)

    assert mock_channel.connection.add_callback_threadsafe.called
    callback = mock_channel.connection.add_callback_threadsafe.call_args[0][0]
    callback()

    mock_channel.basic_ack.assert_called_once_with(delivery_tag)
    mock_extra_func.assert_called_once()


def test_threadsafe_ack_without_extra_func(mock_channel):
    """Test threadsafe_ack without an extra function."""
    delivery_tag = 123

    threadsafe_ack(mock_channel, delivery_tag)

    assert mock_channel.connection.add_callback_threadsafe.called
    callback = mock_channel.connection.add_callback_threadsafe.call_args[0][0]
    callback()

    mock_channel.basic_ack.assert_called_once_with(delivery_tag)


def test_threadsafe_nack(mock_channel):
    """Test threadsafe_nack functionality."""
    delivery_tag = 123
    requeue = True
    mock_extra_func = MagicMock()

    threadsafe_nack(mock_channel, delivery_tag, extra_func=mock_extra_func, requeue=requeue)

    assert mock_channel.connection.add_callback_threadsafe.called
    callback = mock_channel.connection.add_callback_threadsafe.call_args[0][0]
    callback()

    mock_channel.basic_nack.assert_called_once_with(delivery_tag, requeue=requeue)
    mock_extra_func.assert_called_once()


def test_threadsafe_nack_without_extra_func(mock_channel):
    """Test threadsafe_nack without an extra function."""
    delivery_tag = 123
    requeue = False

    threadsafe_nack(mock_channel, delivery_tag, requeue=requeue)

    assert mock_channel.connection.add_callback_threadsafe.called
    callback = mock_channel.connection.add_callback_threadsafe.call_args[0][0]
    callback()

    mock_channel.basic_nack.assert_called_once_with(delivery_tag, requeue=requeue)
