"""Proto package - chat_pb2 and chat_pb2_grpc for gRPC services."""

from . import chat_pb2
import sys

# chat_pb2_grpc does "import chat_pb2" - register so it resolves
sys.modules["chat_pb2"] = chat_pb2
from . import chat_pb2_grpc
sys.modules["chat_pb2_grpc"] = chat_pb2_grpc
