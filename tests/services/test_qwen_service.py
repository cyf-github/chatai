"""Tests for Qwen gRPC service."""

import importlib.util
import os
import sys

# Ensure project root and proto in path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_PROTO = os.path.join(_ROOT, "proto")
for p in (_ROOT, _PROTO):
    if p not in sys.path:
        sys.path.insert(0, p)

from unittest.mock import patch, MagicMock

from proto import chat_pb2


def _load_qwen_servicer():
    """Load QwenServiceServicer (avoids tests.services vs services conflict)."""
    path = os.path.join(_ROOT, "services", "qwen_service", "server.py")
    spec = importlib.util.spec_from_file_location("qwen_server", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["qwen_server"] = mod
    spec.loader.exec_module(mod)
    return mod.QwenServiceServicer


def test_qwen_service_chat_returns_response():
    """Chat returns reply from Qwen/dashscope completion."""
    with patch("dashscope.Generation") as MockGeneration:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output.choices = [
            MagicMock(message=MagicMock(content="Hello from Qwen!"))
        ]
        MockGeneration.call.return_value = mock_response

        QwenServiceServicer = _load_qwen_servicer()
        servicer = QwenServiceServicer()
        request = chat_pb2.ChatRequest(
            messages=[chat_pb2.Message(role="user", content="hi")]
        )
        response = servicer.Chat(request, None)

    assert response.reply == "Hello from Qwen!"


def test_qwen_service_chat_handles_api_error():
    """Chat returns error_message and empty reply on dashscope API error."""
    with patch("dashscope.Generation") as MockGeneration:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.message = "Rate limit exceeded"
        MockGeneration.call.return_value = mock_response

        QwenServiceServicer = _load_qwen_servicer()
        servicer = QwenServiceServicer()
        request = chat_pb2.ChatRequest(
            messages=[chat_pb2.Message(role="user", content="hi")]
        )
        response = servicer.Chat(request, None)

    assert response.reply == ""
    assert "rate limit" in response.error_message.lower()


def test_qwen_service_chat_validates_empty_messages():
    """Chat returns INVALID_REQUEST when messages is empty."""
    with patch("dashscope.Generation"):
        QwenServiceServicer = _load_qwen_servicer()
        servicer = QwenServiceServicer()
        request = chat_pb2.ChatRequest(messages=[])
        response = servicer.Chat(request, None)

    assert response.reply == ""
    assert response.error_code == "INVALID_REQUEST"
    assert response.error_message == "messages required"
