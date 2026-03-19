"""Qwen gRPC service implementation."""

from http import HTTPStatus

import dashscope
from proto import chat_pb2, chat_pb2_grpc


class QwenServiceServicer(chat_pb2_grpc.QwenServiceServicer):
    """gRPC servicer that forwards chat requests to Qwen via dashscope API."""

    def Chat(self, request: chat_pb2.ChatRequest, context) -> chat_pb2.ChatResponse:
        if not request.messages:
            return chat_pb2.ChatResponse(
                reply="",
                error_code="INVALID_REQUEST",
                error_message="messages required",
            )
        try:
            messages = [{"role": m.role, "content": m.content} for m in request.messages]
            response = dashscope.Generation.call(
                model="qwen-turbo",
                messages=messages,
                result_format="message",
            )
            if response.status_code == HTTPStatus.OK:
                content = response.output.choices[0].message.content or ""
                return chat_pb2.ChatResponse(reply=content)
            return chat_pb2.ChatResponse(
                reply="",
                error_message=getattr(response, "message", str(response.status_code)),
            )
        except Exception as e:
            return chat_pb2.ChatResponse(
                reply="",
                error_message=str(e),
            )


def serve(port: int = 50052) -> None:
    import grpc
    from concurrent.futures import ThreadPoolExecutor
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_QwenServiceServicer_to_server(QwenServiceServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    serve(port)
