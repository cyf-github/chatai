## Why

Users need access to Minimax models alongside existing providers (OpenAI, Qwen, Doubao). Minimax offers competitive Chinese-language models and OpenAI-compatible APIs. Adding it extends model choice without changing the existing chat flow.

## What Changes

- Add a new gRPC `MinimaxService` that forwards chat requests to Minimax API (OpenAI-compatible endpoint)
- Register Minimax in the gateway `SERVICE_MAP` (e.g. as `"d"`)
- Add Minimax option to the Gradio frontend service selector
- Add `services/minimax_service/` with server, tests, and env config (e.g. `MINIMAX_API_KEY`, `MINIMAX_MODEL`)

## Capabilities

### New Capabilities

- `minimax-service`: gRPC service that implements the shared Chat RPC, calls Minimax API via OpenAI-compatible client, and returns ChatResponse. Includes env-based config and error handling consistent with Doubao/Qwen services.

### Modified Capabilities

- (none – gateway and frontend changes are implementation details of wiring the new service)

## Impact

- **Code**: New `services/minimax_service/`, updates to `gateway/main.py`, `frontend/app.py`, proto/grpc generated code (if proto defines MinimaxService)
- **APIs**: New service code `"d"` (or chosen alias) in `/chat` request body
- **Dependencies**: Minimax uses OpenAI-compatible API; `openai` package with `base_url` override, or `minimax-client` if preferred
- **Config**: New env vars `MINIMAX_API_KEY`, `MINIMAX_MODEL` (optional, with default)
