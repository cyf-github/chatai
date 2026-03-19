import grpc

from frontend.grpc_client import ProviderClient, build_request


def test_build_chat_request_includes_metadata():
    req = build_request(
        messages=[("user", "hi")],
        session_id="s1",
        provider="minimax",
        model="MiniMax-M2",
        temperature=0.7,
        max_tokens=256,
    )
    assert req.session_id == "s1"
    assert req.metadata["provider"] == "minimax"
    assert req.metadata["model"] == "MiniMax-M2"
    assert req.metadata["temperature"] == "0.7"
    assert req.metadata["max_tokens"] == "256"
    assert req.messages[0].role == "user"
    assert req.messages[0].content == "hi"


def test_chat_returns_readable_error_on_rpc_failure():
    class FakeRpcError(grpc.RpcError):
        def code(self):
            return grpc.StatusCode.UNAVAILABLE

        def details(self):
            return "dial tcp timeout"

    class FakeStub:
        def Chat(self, _request):
            raise FakeRpcError()

    client = ProviderClient("localhost", 50054, "minimax", stub_factory=lambda _: FakeStub())
    text = client.chat([("user", "ping")], "s1", "MiniMax-M2", 0.7, 256)
    assert "UNAVAILABLE" in text
    assert "dial tcp timeout" in text
