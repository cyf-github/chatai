"""Tests for OpenAI gRPC service."""

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


def _load_openai_servicer():
    """Load OpenAIServiceServicer (avoids tests.services vs services conflict)."""
    path = os.path.join(_ROOT, "services", "openai_service", "server.py")
    spec = importlib.util.spec_from_file_location("openai_server", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["openai_server"] = mod
    spec.loader.exec_module(mod)
    return mod.OpenAIServiceServicer


def test_openai_service_chat_returns_response():
    """Chat returns reply from OpenAI completion."""
    with patch("openai.OpenAI") as MockOpenAI:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Hello!"))]
        )
        MockOpenAI.return_value = mock_instance

        OpenAIServiceServicer = _load_openai_servicer()
        servicer = OpenAIServiceServicer()
        request = chat_pb2.ChatRequest(
            messages=[chat_pb2.Message(role="user", content="hi")]
        )
        response = servicer.Chat(request, None)

    assert response.reply == "Hello!"


def test_openai_service_chat_handles_api_error():
    """Chat returns error_message and empty reply on OpenAI API error."""
    from openai import APIError

    with patch("openai.OpenAI") as MockOpenAI:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.side_effect = APIError(
            "Rate limit exceeded", MagicMock(), body=None
        )
        MockOpenAI.return_value = mock_instance

        OpenAIServiceServicer = _load_openai_servicer()
        servicer = OpenAIServiceServicer()
        request = chat_pb2.ChatRequest(
            messages=[chat_pb2.Message(role="user", content="hi")]
        )
        response = servicer.Chat(request, None)

    assert response.reply == ""
    assert "rate limit" in response.error_message.lower()


def test_openai_service_chat_validates_empty_messages():
    """Chat returns INVALID_REQUEST when messages is empty."""
    with patch("openai.OpenAI"):
        OpenAIServiceServicer = _load_openai_servicer()
        servicer = OpenAIServiceServicer()
        request = chat_pb2.ChatRequest(messages=[])
        response = servicer.Chat(request, None)

    assert response.reply == ""
    assert response.error_code == "INVALID_REQUEST"
    assert response.error_message == "messages required"
