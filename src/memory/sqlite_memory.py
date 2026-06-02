import json
import sqlite3
import time
from typing import Dict, List

import numpy as np
import ollama


class SQLiteMemory:
    """
    Hybrid Memory System:
    - Short-term: messages table
    - Long-term: semantic embeddings (memory_vectors)
    """

    def __init__(
        self, db_path: str = "nexa_memory.db", max_messages_per_session: int = 50
    ):
        self.db_path = db_path
        self.max_messages = max_messages_per_session
        self._init_db()

    # =========================================================
    # INIT DB
    # =========================================================
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Chat messages
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp REAL
        )
        """)

        # Semantic memory
        cursor.execute("""
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
    # EMBEDDINGS
    # =========================================================
    def _embed(self, text: str) -> List[float]:
        res = ollama.embeddings(model="nomic-embed-text", prompt=text)
        return res["embedding"]

    def _cosine(self, a, b):
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    # =========================================================
    # ADD MESSAGE
    # =========================================================
    def add_message(self, session_id: str, role: str, content: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT INTO messages (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
        """,
            (session_id, role, content, time.time()),
        )

        conn.commit()

        # cleanup old messages
        cursor.execute(
            """
        SELECT id FROM messages
        WHERE session_id = ?
        ORDER BY id DESC
        """,
            (session_id,),
        )

        rows = cursor.fetchall()

        if len(rows) > self.max_messages:
            old_ids = [r[0] for r in rows[self.max_messages :]]

            cursor.executemany(
                "DELETE FROM messages WHERE id = ?", [(i,) for i in old_ids]
            )
            conn.commit()

        conn.close()

    # =========================================================
    # GET MESSAGES
    # =========================================================
    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT role, content, timestamp
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        LIMIT ?
        """,
            (session_id, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows]

    # =========================================================
    # FORMAT (SHORT-TERM MEMORY)
    # =========================================================
    def format_for_llm(self, session_id: str, limit: int = 20) -> str:
        messages = self.get_messages(session_id, limit)
        return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)

    # =========================================================
    # CLEAR SESSION
    # =========================================================
    def clear_session(self, session_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    # =========================================================
    # SEMANTIC MEMORY STORAGE
    # =========================================================
    def add_semantic_memory(self, session_id: str, content: str):
        embedding = self._embed(content)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT INTO memory_vectors (session_id, content, embedding, timestamp)
        VALUES (?, ?, ?, ?)
        """,
            (session_id, content, json.dumps(embedding), time.time()),
        )

        conn.commit()
        conn.close()

    # =========================================================
    # SEMANTIC SEARCH
    # =========================================================
    def search_semantic_memory(self, session_id: str, query: str, top_k: int = 5):
        query_emb = self._embed(query)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT content, embedding
        FROM memory_vectors
        WHERE session_id = ?
        """,
            (session_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        scored = []

        for content, emb in rows:
            emb_vec = json.loads(emb)
            score = self._cosine(query_emb, emb_vec)
            scored.append((score, content))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [c for _, c in scored[:top_k]]
