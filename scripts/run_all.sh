#!/usr/bin/env bash
# Start all services for the Gradio chat frontend.
# Run from project root: ./scripts/run_all.sh
#
# Architecture: Gradio (7860) -> Gateway (8000) -> gRPC backends (50051/50052/50053/50054)
# Each service runs in the foreground in this script; use separate terminals for production.

set -e
cd "$(dirname "$0")/.."

echo "=== Gradio Chatbot - Starting services ==="
echo "Ports: Service A=50051, B=50052, C=50053, D=50054, Gateway=8000, Gradio=7860"
echo ""

# Start backends in background
echo "[1/6] Starting Service A (OpenAI) on 50051..."
python -m services.openai_service.server 50051 &
PID_A=$!

echo "[2/6] Starting Service B (Qwen) on 50052..."
python -m services.qwen_service.server 50052 &
PID_B=$!

echo "[3/6] Starting Service C (Doubao) on 50053..."
python -m services.doubao_service.server 50053 &
PID_C=$!

echo "[4/6] Starting Service D (Minimax) on 50054..."
python -m services.minimax_service.server 50054 &
PID_D=$!

echo "[5/6] Starting Gateway on 8000..."
uvicorn gateway.main:app --host 0.0.0.0 --port 8000 &
PID_GW=$!

sleep 2

echo "[6/6] Starting Gradio frontend on 7860..."
python -m frontend.app

# If Gradio exits, kill background processes
kill $PID_A $PID_B $PID_C $PID_D $PID_GW 2>/dev/null || true
