"""Gateway FastAPI app: HTTP /chat routes to gRPC services."""

from __future__ import annotations

import os
import sys

import grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PROTO = os.path.join(_ROOT, "proto")
if _PROTO not in sys.path:
    sys.path.insert(0, _PROTO)

import chat_pb2
import chat_pb2_grpc

# service "a"|"b"|"c" -> (host:port, stub_class)
SERVICE_MAP = {
    "a": ("localhost", 50051, chat_pb2_grpc.OpenAIServiceStub),
    "b": ("localhost", 50052, chat_pb2_grpc.QwenServiceStub),
    "c": ("localhost", 50053, chat_pb2_grpc.DoubaoServiceStub),
}


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatBody(BaseModel):
    service: str
    messages: list[ChatMessage]


def create_app() -> FastAPI:
    app = FastAPI(title="Gateway")

    @app.post("/chat")
    def chat(body: ChatBody):
        service = (body.service or "").strip().lower()
        if service not in SERVICE_MAP:
            raise HTTPException(status_code=400, detail="Invalid service")
        if not body.messages:
            raise HTTPException(status_code=400, detail="Empty messages")

        host, port, stub_cls = SERVICE_MAP[service]
        req = chat_pb2.ChatRequest()
        for m in body.messages:
            req.messages.append(chat_pb2.Message(role=m.role, content=m.content))

        channel = grpc.insecure_channel(f"{host}:{port}")
        try:
            stub = stub_cls(channel)
            resp = stub.Chat(req)
            return {"content": resp.reply}
        except grpc.RpcError:
            raise HTTPException(status_code=503, detail="gRPC error")
        finally:
            channel.close()

    return app
