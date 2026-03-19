from frontend.session_store import SessionStore


def test_create_switch_rename_delete_session():
    store = SessionStore()
    sid1 = store.create_session("Session 1")
    sid2 = store.create_session("Session 2")

    assert store.active_session_id == sid2

    store.switch_session(sid1)
    assert store.active_session_id == sid1

    store.rename_session(sid1, "Renamed")
    assert store.sessions[sid1].title == "Renamed"

    store.delete_session(sid2)
    assert sid2 not in store.sessions


def test_messages_are_isolated_per_session():
    store = SessionStore()
    sid1 = store.create_session("A")
    sid2 = store.create_session("B")

    store.append_message(sid1, "user", "hello")
    store.append_message(sid2, "user", "world")

    assert len(store.sessions[sid1].messages) == 1
    assert len(store.sessions[sid2].messages) == 1
