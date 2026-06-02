from typing import Any, Dict


class BudgetManager:
    """
    💰 Token + cost control layer
    Prevents runaway LLM usage
    """

    def __init__(self, max_tokens: int = 4000, max_cost: float = 0.01):
        self.max_tokens = max_tokens
        self.max_cost = max_cost

        self.used_tokens = 0
        self.used_cost = 0.0

    def estimate_tokens(self, text: str) -> int:
        # simple heuristic (MVP)
        return len(text.split())

    def can_proceed(self, text: str, estimated_cost: float) -> Dict[str, Any]:
        tokens = self.estimate_tokens(text)

        if self.used_tokens + tokens > self.max_tokens:
            return {
                "allowed": False,
                "reason": "Token budget exceeded",
            }

        if self.used_cost + estimated_cost > self.max_cost:
            return {
                "allowed": False,
                "reason": "Cost budget exceeded",
            }

        return {"allowed": True, "reason": "OK"}

    def update_usage(self, text: str, cost: float):
        tokens = self.estimate_tokens(text)

        self.used_tokens += tokens
        self.used_cost += cost

    def summary(self):
        return {
            "used_tokens": self.used_tokens,
            "used_cost": round(self.used_cost, 6),
        }
