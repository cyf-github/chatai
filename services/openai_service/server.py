"""OpenAI gRPC service implementation."""

import os

from openai import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)
from proto import chat_pb2, chat_pb2_grpc


class OpenAIServiceServicer(chat_pb2_grpc.OpenAIServiceServicer):
    """gRPC servicer that forwards chat requests to OpenAI API."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

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
                model="gpt-3.5-turbo",
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            return chat_pb2.ChatResponse(reply=content)
        except (APIError, RateLimitError, APIConnectionError, APITimeoutError) as e:
            return chat_pb2.ChatResponse(
                reply="",
                error_message=str(e),
            )


def serve(port: int = 50051) -> None:
    import grpc
    from concurrent.futures import ThreadPoolExecutor
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_OpenAIServiceServicer_to_server(OpenAIServiceServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50051
    serve(port)
