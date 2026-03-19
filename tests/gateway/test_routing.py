"""Tests for Gateway HTTP API routing."""

from fastapi.testclient import TestClient

from gateway.main import create_app


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

