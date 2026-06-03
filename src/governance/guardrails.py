import re
from typing import Any, Dict


class Guardrails:
    """
    🛡️ NexusMind Safety Layer (EventBus-Aligned Final)

    ROLE:
    - Pure validation layer
    - No streaming, no side-effects
    - Used by Orchestrator only

    Covers:
    - Prompt injection detection
    - Query validation
    - Context validation
    - Embedding validation
    """

    def __init__(self):
        # -------------------------
        # PRECOMPILED PATTERNS (PERF OPTIMIZED)
        # -------------------------
        self.block_patterns = [
            re.compile(r"ignore previous instructions"),
            re.compile(r"system prompt"),
            re.compile(r"reveal.*prompt"),
            re.compile(r"act as.*system"),
            re.compile(r"jailbreak"),
            re.compile(r"developer mode"),
            re.compile(r"you are now"),
            re.compile(r"override rules"),
        ]

        # -------------------------
        # LIMITS
        # -------------------------
        self.max_query_len = 5000
        self.max_context_len = 20000

    # =========================================================
    # QUERY VALIDATION (ENTRY GATE)
    # =========================================================
    def validate_query(self, query: Any) -> Dict[str, Any]:
        if query is None:
            return {"safe": False, "reason": "Query is None"}

        if not isinstance(query, str):
            return {"safe": False, "reason": "Query must be a string"}

        query = query.strip()

        if not query:
            return {"safe": False, "reason": "Empty query"}

        if len(query) > self.max_query_len:
            return {"safe": False, "reason": "Query too long"}

        q_lower = query.lower()

        for pattern in self.block_patterns:
            if pattern.search(q_lower):
                return {
                    "safe": False,
                    "reason": f"Blocked prompt injection pattern: {pattern.pattern}",
                }

        return {"safe": True, "reason": "OK"}

    # =========================================================
    # CONTEXT VALIDATION (RAG SAFETY)
    # =========================================================
    def validate_context(self, context: Any) -> Dict[str, Any]:
        if context is None:
            return {"safe": True, "reason": "Empty context"}

        if not isinstance(context, str):
            return {"safe": False, "reason": "Context must be string"}

        if len(context) > self.max_context_len:
            return {
                "safe": False,
                "reason": "Context too large (possible overflow/injection)",
            }

        return {"safe": True, "reason": "OK"}

    # =========================================================
    # EMBEDDING VALIDATION (CRITICAL FOR RAG)
    # =========================================================
    def validate_embedding(self, embedding: Any, expected_dim: int) -> Dict[str, Any]:
        if embedding is None:
            return {"safe": False, "reason": "Embedding is None"}

        if not isinstance(embedding, list):
            return {"safe": False, "reason": "Embedding must be list"}

        if expected_dim and len(embedding) != expected_dim:
            return {
                "safe": False,
                "reason": (
                    f"Embedding dimension mismatch: got {len(embedding)} "
                    f"expected {expected_dim}"
                ),
            }

        return {"safe": True, "reason": "OK"}

    # =========================================================
    # SAFE CHECK HELPER
    # =========================================================
    def safe(self, result: Dict[str, Any]) -> bool:
        return bool(result and result.get("safe", False))

    # =========================================================
    # SANITIZER (OPTIONAL)
    # =========================================================
    def sanitize(self, text: str) -> str:
        if not isinstance(text, str):
            return ""

        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text
