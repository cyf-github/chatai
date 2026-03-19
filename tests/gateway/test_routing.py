"""Tests for Gateway HTTP API routing."""

from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from gateway.main import create_app
from proto import chat_pb2


def test_chat_route_returns_400_for_invalid_service():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"service": "invalid", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert response.status_code == 400


def test_chat_route_returns_400_for_empty_messages():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"service": "a", "messages": []},
    )
    assert response.status_code == 400


def test_chat_route_accepts_service_d():
    """Gateway routes service='d' (Minimax) correctly when gRPC responds."""
    mock_response = chat_pb2.ChatResponse(reply="Hello from Minimax!")

    def fake_unary_unary(*_args, **_kwargs):
        def _handler(request, timeout=None, metadata=None):
            return mock_response
        return _handler

    mock_channel = MagicMock()
    mock_channel.unary_unary = MagicMock(return_value=fake_unary_unary())

    with patch("gateway.main.grpc.insecure_channel", return_value=mock_channel):
        app = create_app()
        client = TestClient(app)
        response = client.post(
            "/chat",
            json={"service": "d", "messages": [{"role": "user", "content": "hi"}]},
        )

    assert response.status_code == 200
    assert response.json().get("content") == "Hello from Minimax!"

