import re
from typing import Any, Dict


class Guardrails:
    """
    🛡️ Safety + validation layer before LLM execution
    """

    def __init__(self):
        # basic unsafe patterns (expand later)
        self.block_patterns = [
            r"ignore previous instructions",
            r"system prompt",
            r"reveal.*prompt",
        ]

    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Returns:
        {
            "safe": bool,
            "reason": str
        }
        """

        q = query.lower()

        for pattern in self.block_patterns:
            if re.search(pattern, q):
                return {
                    "safe": False,
                    "reason": f"Blocked pattern detected: {pattern}",
                }

        return {"safe": True, "reason": "OK"}

    def validate_context(self, context: str) -> Dict[str, Any]:
        """
        Basic sanity check for injected context
        """

        if len(context) > 20000:
            return {
                "safe": False,
                "reason": "Context too large (possible injection or overflow)",
            }

        return {"safe": True, "reason": "OK"}
