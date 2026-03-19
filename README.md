# chatai

Gradio frontend for multi-provider gRPC chat services.

## Running / 启动

Architecture: **Gradio (HTTP)** → **Gateway (FastAPI)** → **gRPC backends (A/B/C/D)**

| Component | Port | Description |
|-----------|------|-------------|
| Service A (OpenAI) | 50051 | gRPC backend |
| Service B (Qwen) | 50052 | gRPC backend |
| Service C (Doubao) | 50053 | gRPC backend |
| Service D (Minimax) | 50054 | gRPC backend |
| Gateway | 8000 | HTTP → gRPC routing |
| Gradio | 7860 | Web UI |

### Quick start (all-in-one)

**Linux/macOS:**
```bash
./scripts/run_all.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\run_all.ps1
```

### Manual startup (separate terminals)

Start in this order:

1. **Backend A (OpenAI)** — requires `OPENAI_API_KEY`:
   ```bash
   python -m services.openai_service.server 50051
   ```

2. **Backend B (Qwen)** — requires `DASHSCOPE_API_KEY`:
   ```bash
   python -m services.qwen_service.server 50052
   ```

3. **Backend C (Doubao)** — requires `DOUBAO_API_KEY`:
   ```bash
   python -m services.doubao_service.server 50053
   ```

4. **Backend D (Minimax)** — requires `MINIMAX_API_KEY`:
   ```bash
   python -m services.minimax_service.server 50054
   ```

5. **Gateway:**
   ```bash
   uvicorn gateway.main:app --host 0.0.0.0 --port 8000
   ```

5. **Gradio frontend:**
   ```bash
   python -m frontend.app
   ```

Then open http://localhost:7860 and choose service `a`, `b`, `c`, or `d` in the UI.

### Environment variables

| Variable | Required for | Description |
|----------|--------------|-------------|
| `OPENAI_API_KEY` | Service A | OpenAI API key |
| `DASHSCOPE_API_KEY` | Service B | Alibaba DashScope (Qwen) API key |
| `DOUBAO_API_KEY` | Service C | Doubao/Volcengine Ark API key |
| `MINIMAX_API_KEY` | Service D | Minimax API key |
| `MINIMAX_MODEL` | Service D | Model name (default: `M2-her`) |
| `GRADIO_GATEWAY_URL` | Gradio | Gateway URL (default: `http://localhost:8000`) |

---

## Frontend variants

### Simple frontend (Gateway-based)

```bash
python -m frontend.app
```

Uses HTTP to Gateway; choose service `a`/`b`/`c`/`d` in the UI.

### Full frontend (direct gRPC)

```bash
python -m frontend.main
```

Optional environment variables:

- `FRONTEND_HOST` (default `127.0.0.1`)
- `FRONTEND_PORT` (default `7860`)

In UI:

- choose provider: `openai`, `qwen`, `doubao`, `minimax`
- set target host and port
- tune model / temperature / max tokens
- manage multiple in-memory chat sessions
