from frontend.session_store import SessionStore
from frontend.gradio_app import handle_send, handle_switch_session


def _seeded_state():
    store = SessionStore()
    sid1 = store.create_session("Session A")
    store.append_message(sid1, "user", "hi A")
    store.append_message(sid1, "assistant", "reply A")
    sid2 = store.create_session("Session B")
    store.append_message(sid2, "user", "hi B")
    store.append_message(sid2, "assistant", "reply B")
    return {"store": store, "active_session_id": sid2, "chat_view": []}


def test_send_message_updates_chat_history():
    state = _seeded_state()

    def fake_chat(_messages, _session_id, _model, _temperature, _max_tokens):
        return "mock assistant"

    chat, updated_state = handle_send(
        user_text="hello",
        provider="minimax",
        host="localhost",
        port=50054,
        model="MiniMax-M2",
        temperature=0.7,
        max_tokens=256,
        state=state,
        chat_fn_factory=lambda *_args, **_kwargs: fake_chat,
    )
    assert chat[-1] == ("hello", "mock assistant")
    active_sid = updated_state["active_session_id"]
    messages = updated_state["store"].sessions[active_sid].messages
    assert messages[-2].content == "hello"
    assert messages[-1].content == "mock assistant"


def test_switch_session_changes_displayed_messages():
    state = _seeded_state()
    store = state["store"]
    session_ids = list(store.sessions.keys())
    first_sid = session_ids[0]

    chat, updated_state = handle_switch_session(first_sid, state)

    assert updated_state["active_session_id"] == first_sid
    assert chat[0] == ("hi A", "reply A")
