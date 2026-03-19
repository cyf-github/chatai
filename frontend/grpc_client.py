"""gRPC client wrapper for provider chat calls."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable

import grpc

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PROTO = os.path.join(_ROOT, "proto")
if _PROTO not in sys.path:
    sys.path.insert(0, _PROTO)

import chat_pb2
import chat_pb2_grpc

DEFAULT_PROVIDER_PORTS = {
    "openai": 50051,
    "qwen": 50052,
    "doubao": 50053,
    "minimax": 50054,
}


def build_request(
    messages: list[tuple[str, str]],
    session_id: str,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> chat_pb2.ChatRequest:
    req = chat_pb2.ChatRequest(session_id=session_id)
    for role, content in messages:
        req.messages.append(chat_pb2.Message(role=role, content=content))
    req.metadata["provider"] = provider
    req.metadata["model"] = model
    req.metadata["temperature"] = str(temperature)
    req.metadata["max_tokens"] = str(max_tokens)
    req.metadata["session_id"] = session_id
    return req


def _default_stub_factory(provider: str) -> Callable[[grpc.Channel], object]:
    mapping = {
        "openai": getattr(chat_pb2_grpc, "OpenAIServiceStub", None),
        "qwen": getattr(chat_pb2_grpc, "QwenServiceStub", None),
        "doubao": getattr(chat_pb2_grpc, "DoubaoServiceStub", None),
        "minimax": getattr(chat_pb2_grpc, "MinMaxServiceStub", None),
    }
    constructor = mapping.get(provider)
    if constructor is None and provider == "minimax":
        return lambda channel: _DirectUnaryStub(
            channel.unary_unary(
                "/chat.MinMaxService/Chat",
                request_serializer=chat_pb2.ChatRequest.SerializeToString,
                response_deserializer=chat_pb2.ChatResponse.FromString,
            )
        )
    if constructor is None:
        raise ValueError(f"Unsupported provider: {provider}")
    return constructor


class _DirectUnaryStub:
    def __init__(self, call: Callable[[chat_pb2.ChatRequest], chat_pb2.ChatResponse]):
        self.Chat = call


class ProviderClient:
    def __init__(
        self,
        host: str,
        port: int | None,
        provider: str,
        stub_factory: Callable[[grpc.Channel], object] | None = None,
    ) -> None:
        self.host = (host or "localhost").strip() or "localhost"
        self.provider = (provider or "openai").strip().lower()
        self.port = int(port or DEFAULT_PROVIDER_PORTS.get(self.provider, 50051))
        chosen_factory = stub_factory or _default_stub_factory(self.provider)
        self._stub_factory = chosen_factory

    def chat(
        self,
        messages: list[tuple[str, str]],
        session_id: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        request = build_request(
            messages=messages,
            session_id=session_id,
            provider=self.provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        try:
            stub = self._stub_factory(channel)
            response = stub.Chat(request)
            if response.error_code or response.error_message:
                return f"Provider error: {response.error_code} {response.error_message}".strip()
            return response.reply or ""
        except grpc.RpcError as exc:
            code = exc.code() if hasattr(exc, "code") else "UNKNOWN"
            details = exc.details() if hasattr(exc, "details") else str(exc)
            return f"RPC {code}: {details}"
        finally:
            channel.close()
