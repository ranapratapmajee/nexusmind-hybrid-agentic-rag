import re
from typing import Any, Dict


class Guardrails:
    """
    🛡️ NexusMind Safety Layer (Production)

    Covers:
    - Prompt injection detection
    - Query validation
    - Context validation (RAG safety)
    - Embedding validation (critical for Chroma)
    - Lightweight orchestrator-safe checks
    """

    def __init__(self):
        # Prompt injection / jailbreak patterns
        self.block_patterns = [
            r"ignore previous instructions",
            r"system prompt",
            r"reveal.*prompt",
            r"act as.*system",
            r"jailbreak",
            r"developer mode",
            r"you are now",
            r"override rules",
        ]

        # hard limits (can later move to config.yaml)
        self.max_query_len = 5000
        self.max_context_len = 20000

    # =========================================================
    # QUERY VALIDATION (ENTRY GATE)
    # =========================================================
    def validate_query(self, query: Any) -> Dict[str, Any]:
        """
        Validates user input before Planner / Router / RAG
        """

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
            if re.search(pattern, q_lower):
                return {
                    "safe": False,
                    "reason": f"Blocked prompt injection pattern: {pattern}",
                }

        return {"safe": True, "reason": "OK"}

    # =========================================================
    # CONTEXT VALIDATION (RAG OUTPUT SAFETY)
    # =========================================================
    def validate_context(self, context: Any) -> Dict[str, Any]:
        """
        Ensures retrieved RAG context is safe & bounded
        """

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
    # EMBEDDING VALIDATION (CRITICAL FOR RAG + CHROMA)
    # =========================================================
    def validate_embedding(self, embedding: Any, expected_dim: int) -> Dict[str, Any]:
        """
        Prevents:
        - Chroma dimension mismatch crash
        - ingestion corruption
        - query-time embedding mismatch
        """

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
    # SAFE CHECK WRAPPER (FOR ORCHESTRATOR)
    # =========================================================
    def safe(self, result: Dict[str, Any]) -> bool:
        """
        Quick boolean helper for pipeline decisions
        """
        return bool(result and result.get("safe", False))

    # =========================================================
    # SIMPLE PROMPT SANITIZER (OPTIONAL UTILITY)
    # =========================================================
    def sanitize(self, text: str) -> str:
        """
        Light cleanup before LLM / embedding
        """
        if not isinstance(text, str):
            return ""

        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text
