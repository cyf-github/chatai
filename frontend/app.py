"""Gradio chat frontend: HTTP client to Gateway."""

from __future__ import annotations

import os

import gradio as gr
import httpx

GATEWAY_URL = os.environ.get("GRADIO_GATEWAY_URL", "http://localhost:8000")


def chat_fn(message, history, service):
    # history: [[user, bot], ...] (tuples format)
    history = history or []
    messages = []
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})
    try:
        r = httpx.post(
            f"{GATEWAY_URL}/chat",
            json={"service": service, "messages": messages},
            timeout=60,
        )
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
