import json
import sqlite3
import time
from collections import defaultdict, deque
from typing import Dict, List

import numpy as np
import ollama


class Memory:
    """
    🧠 NexusMind Unified Memory System (EVENTBUS-ALIGNED FINAL)

    ROLE:
    -----------------------------------------
    1. Short-term memory (RAM cache for fast UI)
    2. Persistent memory (SQLite storage)
    3. Semantic memory (vector embeddings)

    RULE:
    - Memory = PURE DATA LAYER
    - NO orchestration
    - NO prompt building
    - NO EventBus coupling
    """

    def __init__(self, db_path: str = "nexa_memory.db", max_messages: int = 50):
        self.db_path = db_path
        self.max_messages = max_messages

        # -------------------------
        # FAST RAM CACHE (UI LAYER)
        # -------------------------
        self.sessions: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_messages)
        )

        self._init_db()

    # =========================================================
    # DB INIT
    # =========================================================
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Chat messages
        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp REAL
        )
        """)

        # Semantic memory
        cur.execute("""
        CREATE TABLE IF NOT EXISTS memory_vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            content TEXT,
            embedding TEXT,
            timestamp REAL
        )
        """)

        conn.commit()
        conn.close()

    # =========================================================
    # ADD MESSAGE (RAM + SQLITE)
    # =========================================================
    def add_message(self, session_id: str, role: str, content: str):
        msg = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
        }

        # RAM cache
        self.sessions[session_id].append(msg)

        # SQLite persistence
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO messages VALUES (NULL,?,?,?,?)",
            (session_id, role, content, msg["timestamp"]),
        )

        conn.commit()
        conn.close()

    # =========================================================
    # SHORT-TERM MEMORY (RAM)
    # =========================================================
    def get_messages(self, session_id: str, limit: int = 20) -> List[dict]:
        return list(self.sessions.get(session_id, []))[-limit:]

    # =========================================================
    # LONG-TERM MEMORY (DB)
    # =========================================================
    def get_messages_db(self, session_id: str, limit: int = 20) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT role, content, timestamp
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (session_id, limit),
        )

        rows = cur.fetchall()
        conn.close()

        return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows]

    # =========================================================
    # CHAT HISTORY (LLM-READY FORMAT)
    # =========================================================
    def get_chat_history(self, session_id: str, limit: int = 20) -> str:
        msgs = self.get_messages(session_id, limit)
        return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in msgs).strip()

    # =========================================================
    # EMBEDDING MODEL
    # =========================================================
    def _embed(self, text: str) -> List[float]:
        return ollama.embeddings(
            model="nomic-embed-text",
            prompt=text,
        )["embedding"]

    # =========================================================
    # ADD SEMANTIC MEMORY
    # =========================================================
    def add_semantic(self, session_id: str, content: str):
        emb = self._embed(content)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO memory_vectors VALUES (NULL,?,?,?,?)",
            (session_id, content, json.dumps(emb), time.time()),
        )

        conn.commit()
        conn.close()

    # =========================================================
    # SEMANTIC SEARCH
    # =========================================================
    def search_semantic(self, session_id: str, query: str, top_k: int = 5):
        query_emb = self._embed(query)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT content, embedding
            FROM memory_vectors
            WHERE session_id = ?
            """,
            (session_id,),
        )

        rows = cur.fetchall()
        conn.close()

        scored = []

        for content, emb in rows:
            emb_vec = json.loads(emb)

            score = float(
                np.dot(query_emb, emb_vec)
                / (np.linalg.norm(query_emb) * np.linalg.norm(emb_vec))
            )

            scored.append((score, content))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [c for _, c in scored[:top_k]]

    # =========================================================
    # CLEAR SESSION
    # =========================================================
    def clear_session(self, session_id: str):
        # clear RAM
        self.sessions.pop(session_id, None)

        # clear DB
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM messages WHERE session_id=?",
            (session_id,),
        )

        cur.execute(
            "DELETE FROM memory_vectors WHERE session_id=?",
            (session_id,),
        )

        conn.commit()
        conn.close()
