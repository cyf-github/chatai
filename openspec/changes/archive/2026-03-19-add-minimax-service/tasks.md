## 1. Proto and gRPC

- [x] 1.1 Ensure `chat.proto` defines MinimaxService (or MinMaxService); add service block if missing
- [x] 1.2 Regenerate `proto/chat_pb2.py` and `proto/chat_pb2_grpc.py` with `python -m grpc_tools.protoc` so MinMaxServiceServicer and MinMaxServiceStub exist

## 2. Minimax Service Backend

- [x] 2.1 Create `services/minimax_service/__init__.py`
- [x] 2.2 Create `services/minimax_service/server.py` implementing MinMaxServiceServicer, using `openai.OpenAI(base_url="https://api.minimax.io/v1", api_key=...)`, env vars `MINIMAX_API_KEY` and `MINIMAX_MODEL` (default `M2-her`), port 50054
- [x] 2.3 Add `tests/services/test_minimax_service.py` with tests for successful chat, empty messages, and API error handling

## 3. Gateway and Frontend

- [x] 3.1 Add Minimax to `gateway/main.py` SERVICE_MAP as `"d"` -> (localhost, 50054, MinMaxServiceStub)
- [x] 3.2 Add `"d"` to frontend `app.py` Radio choices with label indicating Minimax (e.g. `["a","b","c","d"]` and update label/choices display)

## 4. Run Scripts and Documentation

- [x] 4.1 Update `scripts/run_all.ps1` and `scripts/run_all.sh` to start Minimax service on 50054
- [x] 4.2 Document `MINIMAX_API_KEY` and `MINIMAX_MODEL` in README or env example

## 5. 测试方案

- [x] 5.1 Minimax 服务单元测试：`test_minimax_service_chat_returns_response`（mock OpenAI 客户端，验证正常返回 reply）
- [x] 5.2 Minimax 服务单元测试：`test_minimax_service_chat_validates_empty_messages`（空 messages 返回 INVALID_REQUEST）
- [x] 5.3 Minimax 服务单元测试：`test_minimax_service_chat_handles_api_error`（API 异常时返回 error_message）
- [x] 5.4 Gateway 测试：新增 `test_chat_route_accepts_service_d`，验证 `service="d"` 时 Gateway 能正确路由（可 mock gRPC 或使用 TestClient + 真实 Minimax 服务）
- [x] 5.5 运行 `pytest tests/` 确保所有测试通过
