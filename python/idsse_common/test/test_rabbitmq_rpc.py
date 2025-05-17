"""Testing for RabbitMqUtils functions"""

# ------------------------------------------------------------------------------
# Created on Thu Feb 27 2025
#
# Copyright (c) 2025 Colorado State University. All rights reserved. (1)
#
# Contributors:
#     Mackenzie Grimes (1)
#
# ------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,missing-class-docstring,too-few-public-methods
# pylint: disable=redefined-outer-name,unused-argument,protected-access,duplicate-code
import json
from typing import NamedTuple
from unittest.mock import Mock
from uuid import UUID

from pytest import fixture, raises, MonkeyPatch
from pika import BasicProperties, BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

from idsse.common.rabbitmq_utils import DIRECT_REPLY_QUEUE, Queue
from idsse.common.rabbitmq_rpc import (
    Conn,
    Consumer,
    Exch,
    Future,
    RabbitMqParams,
    RabbitMqMessage,
    RpcConsumer,
    RpcPublisher,
    RpcResponse,
)


# Example data objects
CONN = Conn("localhost", "/", port=5672, username="user", password="password")
RMQ_PARAMS = RabbitMqParams(
    Exch("test_criteria_exch", "topic"), Queue("test_criteria_queue", "", True, False, True)
)
EXAMPLE_UUID = "b6591cc7-8b33-4cd3-aa22-408c83ac5e3c"


class Method(NamedTuple):
    """Mock of pika.frame.Method"""

    exchange: str = " "
    queue: str = ""
    delivery_tag: int = 0
    routing_key: str = ""


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

    mock_obj = Mock(spec=BlockingChannel, name="MockChannel")
    mock_obj.exchange_declare = Mock(side_effect=mock_exch_declare)
    mock_obj.queue_declare = Mock(side_effect=mock_queue_declare)
    mock_obj.is_open = True
    return mock_obj


@fixture
def mock_connection(mock_channel: Mock) -> Mock:
    """Mock pika.BlockingChannel object"""
    mock_obj = Mock(spec=BlockingConnection, name="MockConnection")
    mock_obj.channel = Mock(return_value=mock_channel)
    return mock_obj


@fixture
def mock_consumer(monkeypatch: MonkeyPatch, mock_connection: Mock, mock_channel: Mock) -> Mock:
    """Mock rabbitmq_utils.Consumer thread instance"""
    mock_obj = Mock(spec=Consumer, name="MockConsumer")
    mock_obj.return_value.is_alive = Mock(return_value=False)  # by default, thread not running
    mock_obj.return_value.connection = mock_connection
    mock_obj.return_value.channel = mock_channel
    # hack pika add_callback_threadsafe to invoke immediately (hides complexity of threading)
    mock_obj.return_value.channel.connection.add_callback_threadsafe = Mock(
        side_effect=lambda cb: cb()
    )

    monkeypatch.setattr("idsse.common.rabbitmq_rpc.Consumer", mock_obj)
    # temporarily need to mock Consumer out of rabbitmq_utils as well, where deprecated Rpc is
    monkeypatch.setattr("idsse.common.rabbitmq_utils.Consumer", mock_obj)
    return mock_obj


@fixture
def mock_uuid(monkeypatch: MonkeyPatch) -> Mock:
    """Always return our example UUID str when UUID() is called"""
    mock_obj = Mock()
    mock_obj.UUID = Mock(side_effect=lambda: UUID(EXAMPLE_UUID))
    mock_obj.uuid4 = Mock(side_effect=lambda: EXAMPLE_UUID)
    monkeypatch.setattr("idsse.common.rabbitmq_rpc.uuid", mock_obj)
    return mock_obj


@fixture
def rpc_thread(mock_consumer: Mock, mock_uuid: Mock) -> RpcPublisher:
    return RpcPublisher(CONN, RMQ_PARAMS.exchange, timeout=5)


# tests
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


def test_send_request_works_without_calling_start(
    rpc_thread: RpcPublisher,
    mock_channel: Mock,
    mock_connection: Mock,
    mock_consumer: Mock,
    monkeypatch: MonkeyPatch,
):
    example_message = {"value": "hello world"}

    # when client calls blocking_publish, manually invoke response callback with a faked message
    # from external service, simulating RMQ call/response
    def mock_blocking_publish(*_args, **_kwargs):
        # build mock message from imaginary external service
        method = Method("", 123)
        props = BasicProperties(content_type="application/json", headers={"rpc": EXAMPLE_UUID})
        body = bytes(json.dumps(example_message), encoding="utf-8")
        rpc_thread._on_response(mock_channel, method, props, body)

    monkeypatch.setattr(
        "idsse.common.rabbitmq_rpc.blocking_publish", Mock(side_effect=mock_blocking_publish)
    )

    result = rpc_thread.send_request(RabbitMqMessage(json.dumps({"fake": "request message"})))
    assert json.loads(result.body) == example_message


def test_send_request_times_out_if_no_response(
    mock_connection: Mock, mock_consumer: Mock, mock_uuid: Mock, monkeypatch: MonkeyPatch
):
    # create client with same parameters, except a very short timeout
    _thread = RpcPublisher(CONN, RMQ_PARAMS.exchange, timeout=0.01)

    # do nothing on message publish
    monkeypatch.setattr(
        "idsse.common.rabbitmq_rpc.blocking_publish",
        Mock(side_effect=lambda *_args, **_kwargs: None),
    )

    with raises(TimeoutError) as exc:
        _thread.send_request(RabbitMqMessage(json.dumps({"data": 123})))
    assert EXAMPLE_UUID not in _thread._pending_requests  # request was cleaned up
    assert exc is not None


def test_send_requests_raises_on_error(rpc_thread: RpcPublisher, mock_channel: Mock):
    # pylint: disable=too-many-arguments
    def mock_basic_publish(exchange, routing_key, body, properties=None, mandatory=False):
        # cause exception for pending request Future
        rpc_thread._pending_requests[EXAMPLE_UUID].set_exception(RuntimeError("Something broke"))

    mock_channel.basic_publish.side_effect = mock_basic_publish

    with raises(RuntimeError):
        _ = rpc_thread.send_request(RabbitMqMessage({"data": 123}))

    assert EXAMPLE_UUID not in rpc_thread._pending_requests  # request was cleaned up


def test_nacks_unrecognized_response(
    rpc_thread: RpcPublisher, mock_connection: Mock, mock_channel: Mock, monkeypatch: MonkeyPatch
):
    rpc_thread._pending_requests = {"abcd": Future()}
    delivery_tag = 123
    props = BasicProperties(content_type="application/json", headers={"rpc": "unknown_id"})
    body = bytes(json.dumps({"data": 123}), encoding="utf-8")

    rpc_thread._on_response(mock_channel, Method(delivery_tag=delivery_tag), props, body)

    # unregistered message was acked with no-op (nothing was done to pending requests)
    mock_channel.basic_ack.assert_called_with(delivery_tag=delivery_tag)
    assert "abcd" in rpc_thread._pending_requests
    assert not rpc_thread._pending_requests["abcd"].done()


def test_rpc_consumer_start_stop(mock_consumer: Mock):
    mock_consumer.return_value.is_alive.return_value = False
    rpc_consumer = RpcConsumer(CONN, RMQ_PARAMS, lambda: None)

    rpc_consumer.start()
    mock_consumer.return_value.start.assert_called_once()

    mock_consumer.return_value.is_alive.return_value = True

    rpc_consumer.stop()
    mock_consumer.return_value.stop.assert_called_once()


def test_rpc_consumer_on_message_ack(mock_channel: Mock, mock_consumer: Mock):
    example_response = RabbitMqMessage(
        '{"response": "bar"}',
        BasicProperties(content_type="application/json", correlation_id="some-correlation-id"),
    )
    mock_on_request = Mock(return_value=RpcResponse(example_response, ack=True))
    inbound_tag = 7
    inbound_rpc_id = "123"
    inbound_reply_to = f"{DIRECT_REPLY_QUEUE}.g1h2AA5yZXBseUA1NTQ3NDU0OQAWaZUAAAAAZ7FK9g=="
    inbound_props = BasicProperties(
        content_type="text/html", headers={"rpc": inbound_rpc_id}, reply_to=inbound_reply_to
    )
    inbound_body = bytes('{"request": "foo"}', encoding="utf-8")
    rpc_consumer = RpcConsumer(CONN, RMQ_PARAMS, mock_on_request)

    rpc_consumer._on_message(
        mock_channel, Method("", "", inbound_tag), inbound_props, inbound_body
    )

    mock_channel.basic_ack.assert_called_once_with(inbound_tag)
    assert mock_channel.basic_publish.call_count == 1
    published_args = mock_channel.basic_publish.call_args[1]
    assert published_args["body"] == example_response.body
    assert published_args["properties"].reply_to == inbound_reply_to
    assert published_args["properties"].content_type == "application/json"
    assert published_args["properties"].correlation_id == "some-correlation-id"
    assert published_args["properties"].headers["rpc"] == inbound_rpc_id


def test_rpc_consumer_on_message_nack(mock_channel: Mock, mock_consumer: Mock):
    example_response = RabbitMqMessage(
        '{"response": "bar"}', BasicProperties(content_type="application/json")
    )
    mock_on_request = Mock(return_value=RpcResponse(example_response, ack=False, requeue=True))
    inbound_tag = 7
    inbound_props = BasicProperties(
        content_type="application/json", headers={"rpc": "123"}, reply_to=DIRECT_REPLY_QUEUE
    )
    inbound_body = bytes('{"request": "foo"}', encoding="utf-8")
    rpc_consumer = RpcConsumer(CONN, RMQ_PARAMS, mock_on_request)

    rpc_consumer._on_message(
        mock_channel, Method("", "", inbound_tag), inbound_props, inbound_body
    )

    mock_channel.basic_nack.assert_called_once_with(inbound_tag, requeue=True)
