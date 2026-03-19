"""Doubao (豆包) gRPC service implementation."""

import os

from volcenginesdkarkruntime import Ark
from proto import chat_pb2, chat_pb2_grpc


class DoubaoServiceServicer(chat_pb2_grpc.DoubaoServiceServicer):
    """gRPC servicer that forwards chat requests to Doubao/豆包 via Volcengine Ark API."""

    def __init__(self) -> None:
        self.client = Ark(api_key=os.environ.get("DOUBAO_API_KEY", ""))
        self.model = os.environ.get("DOUBAO_MODEL", "ep-20240619083846-c4xff")

    def Chat(self, request: chat_pb2.ChatRequest, context) -> chat_pb2.ChatResponse:
        if not request.messages:
            return chat_pb2.ChatResponse(
                reply="",
                error_code="INVALID_REQUEST",
                error_message="messages required",
            )
        try:
            messages = [{"role": m.role, "content": m.content} for m in request.messages]
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            return chat_pb2.ChatResponse(reply=content)
        except Exception as e:
            return chat_pb2.ChatResponse(
                reply="",
                error_message=str(e),
            )
