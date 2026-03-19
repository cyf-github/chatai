# Gradio 聊天机器人设计文档

**日期：** 2026-03-19  
**状态：** 已确认

## 1. 目标

使用 Gradio 实现聊天机器人页面：前端展示会话并支持选择服务 A/B/C，中台 Gateway 做 HTTP→gRPC 路由转发，后端三个 gRPC 服务分别调用 OpenAI、Qwen、豆包。

## 2. 架构

```
┌─────────────┐     HTTP      ┌─────────────┐    gRPC     ┌─────────────────┐
│   Gradio    │ ───────────►  │   Gateway   │ ──────────►  │ Service A       │
│  (前端)     │   POST /chat   │  (中台)     │             │ (OpenAI gRPC)   │
│             │               │             │ ──────────► │ Service B       │
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

## 3. 组件职责

### Gradio 前端
- 界面：Chatbot + 输入框 + 服务选择（Radio/Dropdown：A/B/C）
- 逻辑：发送时 POST 到 Gateway `/chat`，展示回复

### Gateway 中台
- FastAPI，`POST /chat`，根据 `service` 路由到对应 gRPC 后端
- HTTP↔proto 转换，配置各后端 gRPC 地址

### 后端 A/B/C
- 共用 proto，各自实现 Chat：A→OpenAI，B→Qwen，C→豆包

## 4. 数据流

**HTTP 请求：** `{ "service": "a"|"b"|"c", "messages": [{"role","content"}] }`  
**HTTP 响应：** `{ "content": "..." }` 或 `{ "error": "..." }`  
**gRPC：** 沿用现有 ChatRequest/ChatResponse

## 5. 错误处理

- 超时→504；后端不可用→503；无效请求→400；内部异常→500
- API Key 通过环境变量配置

## 6. 测试策略

- 单元测试：Gateway 路由/转换；后端 mock LLM
- 集成测试：Gateway + 至少一个后端
- 手动测试：全进程启动验证
