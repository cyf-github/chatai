# Gradio 多服务聊天机器人 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 Gradio 聊天机器人，用户可选择服务 A/B/C，中台 Gateway 通过 HTTP 接收并路由到 gRPC 后端，后端分别调用 OpenAI、Qwen、豆包。

**Architecture:** Gradio (HTTP) → Gateway (FastAPI, HTTP→gRPC) → 三个 gRPC 后端 (OpenAI/Qwen/豆包)。多进程部署。

**Tech Stack:** Gradio, httpx, FastAPI, grpcio, openai, dashscope, volcengine-python-sdk

---

## Task 1: 项目结构与依赖

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml` (optional, if using)
- Modify: `proto/` (ensure chat_pb2.py exists, or add chat.proto + generate)

**Step 1: 创建 requirements.txt**

```txt
gradio>=4.0
httpx>=0.25
fastapi>=0.100
uvicorn>=0.22
grpcio>=1.78
grpcio-tools>=1.78
openai>=1.0
dashscope>=1.14
volcengine-python-sdk>=1.0
pytest>=7.0
pytest-asyncio>=0.21
```

**Step 2: 确认 proto 可用**

若 `proto/chat_pb2.py` 不存在，需有 `proto/chat.proto` 并执行：
```bash
python -m grpc_tools.protoc -I proto --python_out=proto --grpc_python_out=proto proto/chat.proto
```
ChatRequest 需含 messages (repeated Message)，ChatResponse 需含 content (string) 和可选 error (string)。

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add dependencies for gradio chatbot"
```

---

## Task 2: 后端服务 A (OpenAI)

**Files:**
- Create: `services/openai_service/__init__.py`
- Create: `services/openai_service/server.py`
- Test: `tests/services/test_openai_service.py`

**Step 1: 写失败测试**

```python
# tests/services/test_openai_service.py
import pytest
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, ".")
from proto import chat_pb2

def test_openai_service_chat_returns_response():
    from services.openai_service.server import OpenAIServiceServicer
    servicer = OpenAIServiceServicer()
    request = chat_pb2.ChatRequest(messages=[chat_pb2.Message(role="user", content="hi")])
    with patch("services.openai_service.server.openai") as mock_openai:
        mock_openai.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Hello!"))]
        )
        response = servicer.Chat(request, None)
    assert response.content == "Hello!"
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/services/test_openai_service.py -v`
Expected: FAIL (module/import error)

**Step 3: 最小实现**

```python
# services/openai_service/__init__.py
# empty or from .server import *
```

```python
# services/openai_service/server.py
import os
from openai import OpenAI
from proto import chat_pb2, chat_pb2_grpc

class OpenAIServiceServicer(chat_pb2_grpc.OpenAIServiceServicer):
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

    def Chat(self, request, context):
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        resp = self.client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        content = resp.choices[0].message.content
        return chat_pb2.ChatResponse(content=content)
```

(需根据 proto 实际字段调整，如 Message 结构)

**Step 4: 运行测试确认通过**

**Step 5: Commit**

```bash
git add services/openai_service tests/services/test_openai_service.py
git commit -m "feat: add OpenAI gRPC service"
```

---

## Task 3: 后端服务 B (Qwen)

**Files:**
- Create: `services/qwen_service/__init__.py`
- Create: `services/qwen_service/server.py`
- Test: `tests/services/test_qwen_service.py`

**Step 1: 写失败测试** (类似 Task 2，mock dashscope)

**Step 2–5:** 同上流程，实现 Qwen 服务，使用 `dashscope` 调用 qwen 模型。

---

## Task 4: 后端服务 C (豆包)

**Files:**
- Create: `services/doubao_service/__init__.py`
- Create: `services/doubao_service/server.py`
- Test: `tests/services/test_doubao_service.py`

**Step 1: 写失败测试** (类似 Task 2，mock volcengine)

**Step 2–5:** 同上流程，实现豆包服务，使用 `volcengine-python-sdk` 或官方 API。

---

## Task 5: Gateway 路由与 HTTP API

**Files:**
- Create: `gateway/__init__.py`
- Create: `gateway/main.py`
- Test: `tests/gateway/test_routing.py`

**Step 1: 写失败测试**

```python
# tests/gateway/test_routing.py
from fastapi.testclient import TestClient
from gateway.main import app

def test_chat_route_returns_400_for_invalid_service():
    client = TestClient(app)
    r = client.post("/chat", json={"service": "x", "messages": []})
    assert r.status_code == 400
```

**Step 2: 运行确认失败**

**Step 3: 实现 Gateway**

```python
# gateway/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import grpc
from proto import chat_pb2, chat_pb2_grpc
import os

app = FastAPI()

SERVICE_MAP = {
    "a": ("localhost:50051", chat_pb2_grpc.OpenAIServiceStub),
    "b": ("localhost:50052", chat_pb2_grpc.QwenServiceStub),
    "c": ("localhost:50053", chat_pb2_grpc.DoubaoServiceStub),
}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    service: str
    messages: List[Message]

@app.post("/chat")
def chat(req: ChatRequest):
    if req.service not in SERVICE_MAP:
        raise HTTPException(400, "Invalid service")
    if not req.messages:
        raise HTTPException(400, "messages required")
    addr, stub_cls = SERVICE_MAP[req.service]
    channel = grpc.insecure_channel(addr)
    stub = stub_cls(channel)
    pb_messages = [chat_pb2.Message(role=m.role, content=m.content) for m in req.messages]
    pb_req = chat_pb2.ChatRequest(messages=pb_messages)
    try:
        resp = stub.Chat(pb_req, timeout=60)
        return {"content": resp.content}
    except grpc.RpcError as e:
        raise HTTPException(503, str(e))
```

**Step 4–5:** 运行测试、Commit

---

## Task 6: Gradio 前端

**Files:**
- Create: `frontend/app.py`

**Step 1: 实现 Gradio 界面**

```python
# frontend/app.py
import gradio as gr
import httpx

GATEWAY_URL = "http://localhost:8000"

def chat_fn(message, history, service):
    # history: [[user, bot], ...] (tuples format)
    messages = []
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})
    try:
        r = httpx.post(f"{GATEWAY_URL}/chat", json={"service": service, "messages": messages}, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data.get("content", "") or data.get("error", "无回复")
    except httpx.HTTPStatusError as e:
        return f"请求失败: {e.response.status_code}"
    except Exception as e:
        return f"发送失败: {str(e)}"

with gr.Blocks() as demo:
    service = gr.Radio(choices=["a", "b", "c"], value="a", label="选择服务")
    gr.ChatInterface(fn=chat_fn, additional_inputs=[service], title="多模型聊天")

if __name__ == "__main__":
    demo.launch()
```

**Step 2: 本地验证**

启动 Gateway、至少一个后端、Gradio，手动测试。

**Step 3: Commit**

```bash
git add frontend/app.py
git commit -m "feat: add Gradio chat frontend"
```

---

## Task 7: 启动脚本与文档

**Files:**
- Create: `scripts/run_all.sh` 或 `README.md` 启动说明

**Step 1: 编写启动说明**

说明如何依次启动：后端 A/B/C (各 gRPC 端口) → Gateway (8000) → Gradio (7860)。

**Step 2: Commit**

```bash
git add scripts/ README.md
git commit -m "docs: add run instructions"
```

---

## 执行选项

计划已保存至 `docs/plans/2026-03-19-gradio-chatbot-implementation.md`。两种执行方式：

**1. Subagent-Driven（本会话）** — 按任务派发子 agent，逐任务评审、快速迭代

**2. Parallel Session（新会话）** — 在新会话中使用 executing-plans，批量执行并设置检查点

请选择一种方式。
