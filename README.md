# chatai

Gradio frontend for multi-provider gRPC chat services.

## Frontend (Gradio)

Run:

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
