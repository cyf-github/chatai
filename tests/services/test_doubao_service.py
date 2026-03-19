"""Tests for Doubao gRPC service."""

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


def _load_doubao_servicer():
    """Load DoubaoServiceServicer (avoids tests.services vs services conflict)."""
    path = os.path.join(_ROOT, "services", "doubao_service", "server.py")
    spec = importlib.util.spec_from_file_location("doubao_server", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["doubao_server"] = mod
    spec.loader.exec_module(mod)
    return mod.DoubaoServiceServicer


def test_doubao_service_chat_returns_response():
    """Chat returns reply from Doubao/Ark completion."""
    with patch("volcenginesdkarkruntime.Ark") as MockArk:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Hello from Doubao!"))]
        )
        MockArk.return_value = mock_instance

        DoubaoServiceServicer = _load_doubao_servicer()
        servicer = DoubaoServiceServicer()
        request = chat_pb2.ChatRequest(
            messages=[chat_pb2.Message(role="user", content="hi")]
        )
        response = servicer.Chat(request, None)

    assert response.reply == "Hello from Doubao!"


def test_doubao_service_chat_handles_api_error():
    """Chat returns error_message and empty reply on Doubao/Ark API error."""
    with patch("volcenginesdkarkruntime.Ark") as MockArk:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.side_effect = Exception(
            "Rate limit exceeded"
        )
        MockArk.return_value = mock_instance

        DoubaoServiceServicer = _load_doubao_servicer()
        servicer = DoubaoServiceServicer()
        request = chat_pb2.ChatRequest(
            messages=[chat_pb2.Message(role="user", content="hi")]
        )
        response = servicer.Chat(request, None)

    assert response.reply == ""
    assert "rate limit" in response.error_message.lower()


def test_doubao_service_chat_validates_empty_messages():
    """Chat returns INVALID_REQUEST when messages is empty."""
    with patch("volcenginesdkarkruntime.Ark"):
        DoubaoServiceServicer = _load_doubao_servicer()
        servicer = DoubaoServiceServicer()
        request = chat_pb2.ChatRequest(messages=[])
        response = servicer.Chat(request, None)

    assert response.reply == ""
    assert response.error_code == "INVALID_REQUEST"
    assert response.error_message == "messages required"
