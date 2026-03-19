"""Gradio app entry functions and handlers."""

from __future__ import annotations

from typing import Callable

from frontend.grpc_client import ProviderClient
from frontend.session_store import SessionStore


StateDict = dict[str, object]


def init_state() -> StateDict:
    store = SessionStore()
    sid = store.create_session("New Chat")
    return {"store": store, "active_session_id": sid, "chat_view": []}


def _get_store(state: StateDict) -> SessionStore:
    return state["store"]  # type: ignore[return-value]


def _active_session_id(state: StateDict) -> str:
    sid = state.get("active_session_id")
    if isinstance(sid, str) and sid:
        return sid
    store = _get_store(state)
    sid = store.create_session("New Chat")
    state["active_session_id"] = sid
    return sid


def _chat_pairs(store: SessionStore, session_id: str) -> list[tuple[str, str]]:
    messages = store.sessions[session_id].messages
    pairs: list[tuple[str, str]] = []
    pending_user: str | None = None
    for msg in messages:
        if msg.role == "user":
            if pending_user is not None:
                pairs.append((pending_user, ""))
            pending_user = msg.content
        elif msg.role == "assistant":
            if pending_user is None:
                pairs.append(("", msg.content))
            else:
                pairs.append((pending_user, msg.content))
                pending_user = None
    if pending_user is not None:
        pairs.append((pending_user, ""))
    return pairs


def _default_chat_callable(host: str, port: int, provider: str) -> Callable[..., str]:
    client = ProviderClient(host=host, port=port, provider=provider)
    return client.chat


def handle_new_session(state: StateDict) -> tuple[list[tuple[str, str]], StateDict]:
    store = _get_store(state)
    sid = store.create_session("New Chat")
    state["active_session_id"] = sid
    return _chat_pairs(store, sid), state


def handle_switch_session(session_id: str, state: StateDict) -> tuple[list[tuple[str, str]], StateDict]:
    store = _get_store(state)
    store.switch_session(session_id)
    state["active_session_id"] = session_id
    return _chat_pairs(store, session_id), state


def handle_rename_session(
    session_id: str, new_title: str, state: StateDict
) -> tuple[list[str], StateDict]:
    store = _get_store(state)
    store.rename_session(session_id, new_title)
    return [f"{sid}: {sess.title}" for sid, sess in store.sessions.items()], state


def handle_delete_session(session_id: str, state: StateDict) -> tuple[list[tuple[str, str]], StateDict]:
    store = _get_store(state)
    store.delete_session(session_id)
    sid = store.active_session_id
    if sid is None:
        sid = store.create_session("New Chat")
    state["active_session_id"] = sid
    return _chat_pairs(store, sid), state


def handle_clear_current_session(state: StateDict) -> tuple[list[tuple[str, str]], StateDict]:
    store = _get_store(state)
    sid = _active_session_id(state)
    store.sessions[sid].messages.clear()
    return [], state


def handle_send(
    user_text: str,
    provider: str,
    host: str,
    port: int,
    model: str,
    temperature: float,
    max_tokens: int,
    state: StateDict,
    chat_fn_factory: Callable[..., Callable[..., str]] | None = None,
) -> tuple[list[tuple[str, str]], StateDict]:
    text = (user_text or "").strip()
    if not text:
        sid = _active_session_id(state)
        return _chat_pairs(_get_store(state), sid), state

    store = _get_store(state)
    sid = _active_session_id(state)
    store.append_message(sid, "user", text)

    factory = chat_fn_factory or _default_chat_callable
    chat_fn = factory(host, int(port), provider)
    reply = chat_fn(
        [(m.role, m.content) for m in store.sessions[sid].messages],
        sid,
        model,
        float(temperature),
        int(max_tokens),
    )
    store.append_message(sid, "assistant", reply)
    chat = _chat_pairs(store, sid)
    state["chat_view"] = chat
    return chat, state


def build_app():
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError("gradio is not installed. Run: pip install gradio") from exc

    with gr.Blocks(title="Chatai Frontend") as app:
        # Background meteor animation canvas
        meteor_html = gr.HTML("""
<canvas id="meteorCanvas" style="
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: -1;
    opacity: 0.35;
    pointer-events: none;
"></canvas>
""")
        state = gr.State(init_state())
        with gr.Row():
            with gr.Column(scale=1):
                new_btn = gr.Button("New Session")
                session_id_box = gr.Textbox(label="Session ID")
                switch_btn = gr.Button("Switch Session")
                rename_box = gr.Textbox(label="Rename Current Session")
                rename_btn = gr.Button("Rename")
                delete_btn = gr.Button("Delete Current Session")
            with gr.Column(scale=3):
                provider = gr.Dropdown(
                    choices=["openai", "qwen", "doubao", "minimax"],
                    value="openai",
                    label="Provider",
                )
                host = gr.Textbox(label="Host", value="localhost")
                port = gr.Number(label="Port", value=50051, precision=0)
                model = gr.Textbox(label="Model", value="")
                temperature = gr.Number(label="Temperature", value=0.7)
                max_tokens = gr.Number(label="Max Tokens", value=512, precision=0)
                chatbot = gr.Chatbot(label="Chat")
                user_text = gr.Textbox(label="Message")
                send_btn = gr.Button("Send")
                clear_btn = gr.Button("Clear Current Session")

        new_btn.click(handle_new_session, inputs=[state], outputs=[chatbot, state])
        switch_btn.click(handle_switch_session, inputs=[session_id_box, state], outputs=[chatbot, state])
        rename_btn.click(handle_rename_session, inputs=[session_id_box, rename_box, state], outputs=[session_id_box, state])
        delete_btn.click(handle_delete_session, inputs=[session_id_box, state], outputs=[chatbot, state])
        clear_btn.click(handle_clear_current_session, inputs=[state], outputs=[chatbot, state])
        send_btn.click(
            handle_send,
            inputs=[user_text, provider, host, port, model, temperature, max_tokens, state],
            outputs=[chatbot, state],
        )

    return app
