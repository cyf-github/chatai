## Context

The chat system uses gRPC services (OpenAI, Qwen, Doubao) behind a FastAPI gateway. Each service implements the shared Chat RPC and forwards to its provider API. The Gradio frontend lets users pick a service via Radio (`"a"`, `"b"`, `"c"`). Minimax exposes an OpenAI-compatible API (`base_url=https://api.minimax.io/v1`), so we can reuse the `openai` package. The proto already defines `MinMaxService` in `chat_pb2`; `chat_pb2_grpc` may need regeneration if MinMaxService is missing.

## Goals / Non-Goals

**Goals:**
- Add Minimax as a fourth backend option, selectable in the frontend
- Use OpenAI-compatible client for Minimax (no new SDK)
- Match existing service patterns (env config, error handling, Chat RPC)

**Non-Goals:**
- Streaming, function calling, or other Minimax-specific features
- Changing the shared Chat RPC contract

## Decisions

### 1. Minimax client: OpenAI SDK with base_url override
- **Choice**: Use `openai.OpenAI(base_url="https://api.minimax.io/v1", api_key=...)` for Minimax
- **Rationale**: Minimax docs recommend this; avoids adding `minimax-client`. Same pattern as other OpenAI-compatible providers
- **Alternative**: `minimax-client` — rejected to keep dependencies minimal

### 2. Service code: `"d"`
- **Choice**: Map Minimax to `"d"` in gateway and frontend
- **Rationale**: Follows existing `"a"`/`"b"`/`"c"` convention; no breaking change

### 3. Proto / gRPC: Add MinimaxService if missing, regenerate
- **Choice**: Ensure `chat.proto` defines `MinimaxService` (or `MinMaxService` if proto uses that name), regenerate `chat_pb2_grpc.py` so `MinimaxServiceServicer` / `MinimaxServiceStub` exist
- **Rationale**: `chat_pb2` already references MinMaxService; grpc stubs may be out of date. Regeneration keeps proto and generated code in sync

### 4. Default model: `M2-her`
- **Choice**: Default model `M2-her` (configurable via `MINIMAX_MODEL`)
- **Rationale**: Minimax docs list M2-her as the primary text chat model

### 5. Port: 50054
- **Choice**: Minimax service listens on 50054
- **Rationale**: 50051–50053 used by OpenAI, Qwen, Doubao; next free port

## Risks / Trade-offs

- **[Risk]** Minimax API key or base URL changes → Mitigation: Use env vars; document in README
- **[Risk]** Proto/grpc out of sync → Mitigation: Regenerate with `python -m grpc_tools.protoc` after proto edit
- **[Trade-off]** No streaming → Acceptable for initial integration; can add later if needed
