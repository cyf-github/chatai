"""OpenAI gRPC service implementation."""

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_PROTO = os.path.join(_ROOT, "proto")
if _PROTO not in sys.path:
    sys.path.insert(0, _PROTO)

from openai import OpenAI
import chat_pb2
import chat_pb2_grpc


class OpenAIServiceServicer(chat_pb2_grpc.OpenAIServiceServicer):
    """gRPC servicer that forwards chat requests to OpenAI API."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

    def Chat(self, request: chat_pb2.ChatRequest, context) -> chat_pb2.ChatResponse:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        resp = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        content = resp.choices[0].message.content or ""
        return chat_pb2.ChatResponse(reply=content)
