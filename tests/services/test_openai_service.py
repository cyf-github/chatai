"""Tests for OpenAI gRPC service."""

import importlib.util
import os
import sys
from unittest.mock import patch, MagicMock

# Ensure project root and proto are in path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_PROTO = os.path.join(_ROOT, "proto")
for p in (_ROOT, _PROTO):
    if p not in sys.path:
        sys.path.insert(0, p)

import chat_pb2


def test_openai_service_chat_returns_response():
    """Chat returns reply from OpenAI completion."""
    with patch("openai.OpenAI") as MockOpenAI:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Hello!"))]
        )
        MockOpenAI.return_value = mock_instance

        # Load server module directly to avoid tests.services vs services conflict
        server_path = os.path.join(_ROOT, "services", "openai_service", "server.py")
        spec = importlib.util.spec_from_file_location(
            "openai_server", server_path, submodule_search_locations=[]
        )
        server_mod = importlib.util.module_from_spec(spec)
        sys.modules["openai_server"] = server_mod
        spec.loader.exec_module(server_mod)
        OpenAIServiceServicer = server_mod.OpenAIServiceServicer

        servicer = OpenAIServiceServicer()
        request = chat_pb2.ChatRequest(
            messages=[chat_pb2.Message(role="user", content="hi")]
        )
        response = servicer.Chat(request, None)

    assert response.reply == "Hello!"
