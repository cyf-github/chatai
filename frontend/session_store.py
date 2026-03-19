"""In-memory chat session store."""

from __future__ import annotations

from dataclasses import dataclass, field
import time
import uuid


@dataclass
class Message:
    role: str
    content: str
    ts: float = field(default_factory=time.time)


@dataclass
class Session:
    session_id: str
    title: str
    created_at: float = field(default_factory=time.time)
    messages: list[Message] = field(default_factory=list)


class SessionStore:
    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}
        self.active_session_id: str | None = None

    def create_session(self, title: str | None = None) -> str:
        session_id = uuid.uuid4().hex
        display_title = (title or "").strip() or "New Chat"
        self.sessions[session_id] = Session(session_id=session_id, title=display_title)
        self.active_session_id = session_id
        return session_id

    def switch_session(self, session_id: str) -> None:
        if session_id not in self.sessions:
            raise KeyError(f"Unknown session_id: {session_id}")
        self.active_session_id = session_id

    def rename_session(self, session_id: str, title: str) -> None:
        if session_id not in self.sessions:
            raise KeyError(f"Unknown session_id: {session_id}")
        cleaned = (title or "").strip()
        if cleaned:
            self.sessions[session_id].title = cleaned

    def delete_session(self, session_id: str) -> None:
        if session_id not in self.sessions:
            raise KeyError(f"Unknown session_id: {session_id}")
        del self.sessions[session_id]
        if self.active_session_id == session_id:
            self.active_session_id = next(iter(self.sessions), None)

    def append_message(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self.sessions:
            raise KeyError(f"Unknown session_id: {session_id}")
        session = self.sessions[session_id]
        session.messages.append(Message(role=role, content=content))
        if role == "user" and session.title == "New Chat":
            snippet = (content or "").strip().replace("\n", " ")
            if snippet:
                session.title = snippet[:24]

    def list_sessions(self) -> list[Session]:
        return sorted(self.sessions.values(), key=lambda item: item.created_at)
