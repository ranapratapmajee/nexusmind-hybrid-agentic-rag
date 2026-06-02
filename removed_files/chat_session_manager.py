import time
from collections import defaultdict, deque
from typing import Dict, List, Optional


class ChatSessionManager:
    """
    Persistent chat storage per session.
    Used for UI + long-term conversation history.
    """

    def __init__(self, max_messages: int = 200):
        # bounded memory per session (prevents RAM explosion)
        self.sessions: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_messages)
        )

    # =========================================================
    # CREATE SESSION
    # =========================================================
    def create_session(self, session_id: str = "default") -> str:
        _ = self.sessions[session_id]  # auto-create via defaultdict
        return session_id

    # =========================================================
    # ADD MESSAGE
    # =========================================================
    def add_message(self, session_id: str, role: str, message: str):
        self.sessions[session_id].append(
            {"role": role, "content": message, "timestamp": time.time()}
        )

    # =========================================================
    # GET FULL HISTORY
    # =========================================================
    def get_messages(self, session_id: str) -> List[dict]:
        return list(self.sessions.get(session_id, []))

    # =========================================================
    # GET RECENT MESSAGES (for LLM context building)
    # =========================================================
    def get_recent(self, session_id: str, n: int = 12) -> List[dict]:
        return list(self.sessions.get(session_id, []))[-n:]

    # =========================================================
    # FORMAT FOR LLM (SAFE + CONTROLLED)
    # =========================================================
    def format_for_llm(self, session_id: str, max_messages: int = 12) -> str:
        messages = list(self.sessions.get(session_id, []))[-max_messages:]

        if not messages:
            return ""

        return "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages
        ).strip()

    # =========================================================
    # CLEAR SESSION
    # =========================================================
    def clear_session(self, session_id: str):
        self.sessions[session_id].clear()

    # =========================================================
    # LAST MESSAGE
    # =========================================================
    def last_message(self, session_id: str) -> Optional[dict]:
        messages = self.sessions.get(session_id, [])
        return messages[-1] if messages else None
