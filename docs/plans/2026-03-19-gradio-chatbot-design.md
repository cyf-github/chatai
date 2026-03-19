# Gradio 多服务聊天机器人设计

## 概述

使用 Gradio 实现聊天机器人前端，用户可选择服务 A/B/C，中台 Gateway 通过 HTTP 接收请求并路由到对应 gRPC 后端，后端分别调用 OpenAI、Qwen、豆包 API。

## 架构

```
┌─────────────┐     HTTP      ┌─────────────┐    gRPC     ┌─────────────────┐
│   Gradio    │ ───────────►  │   Gateway   │ ──────────►  │ Service A       │
│  (前端)     │   POST /chat   │  (中台)     │             │ (OpenAI gRPC)   │
│             │               │             │ ──────────►  │ Service B       │
│  - 会话展示  │               │  - 路由转发  │             │ (Qwen gRPC)     │
│  - 服务选择  │               │  - 协议转换  │             │ Service C       │
└─────────────┘               └─────────────┘ ──────────►  │ (豆包 gRPC)      │
                                                          └─────────────────┘
```

**进程划分：**
- 进程 1：Gradio（默认 7860）
- 进程 2：Gateway（如 8000）
- 进程 3–5：Service A / B / C（各自 gRPC 端口）

**技术栈：** Gradio + httpx；Gateway: FastAPI + grpcio；后端：grpcio + 各厂商 SDK

## 组件职责

### Gradio 前端
- 界面：Chatbot + 输入框 + 发送；服务选择：Radio/Dropdown（A/B/C）
- 逻辑：发送时 POST 到 Gateway `/chat`，收到回复追加到 Chatbot

### Gateway 中台
- FastAPI，`POST /chat`，根据 `service` 路由到对应 gRPC 后端
- 协议转换：HTTP messages ↔ proto ChatRequest/ChatResponse

### 后端 A/B/C
- 共用 proto，各自实现 Chat：A→OpenAI，B→Qwen，C→豆包

## 数据流

**HTTP 请求：** `{ "service": "a"|"b"|"c", "messages": [{"role","content"}] }`  
**HTTP 响应：** `{ "content": "..." }` 或 `{ "error": "..." }`  
**gRPC：** 沿用现有 proto ChatRequest/ChatResponse

## 错误处理

- 超时/不可用：504/503，前端提示
- LLM 错误：后端写入 error，Gateway 透传
- 无效请求：400
- API Key：环境变量，缺失时拒绝请求

## 测试策略

- 单元测试：Gateway 路由/转换（mock gRPC）；后端（mock LLM API）
- 集成测试：Gateway + 至少一个后端
- 手动：全进程启动，切换服务验证
