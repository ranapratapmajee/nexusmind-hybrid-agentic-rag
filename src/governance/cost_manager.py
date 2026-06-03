from typing import Any, Dict


class CostManager:
    """
    💰 Unified Token + Cost + Budget Controller

    RESPONSIBILITIES:
    - Token estimation
    - Cost calculation (provider-aware)
    - Budget enforcement
    - Usage tracking
    - EventBus-friendly outputs
    """

    def __init__(self, max_tokens: int = 4000, max_cost: float = 0.01):
        self.max_tokens = max_tokens
        self.max_cost = max_cost

        self.used_tokens = 0
        self.used_cost = 0.0

        # cost per 1K tokens (MVP estimates)
        self.cost_per_1k_tokens = {
            "ollama": 0.0,
            "gemini": 0.0005,
            "openai": 0.01,
            "anthropic": 0.015,
        }

    # =========================================================
    # TOKEN ESTIMATION (SHARED)
    # =========================================================
    def estimate_tokens(self, text: str) -> int:
        if not isinstance(text, str):
            return 0
        return len(text.split())

    # =========================================================
    # COST ESTIMATION
    # =========================================================
    def estimate_cost(self, provider: str, text: str) -> float:
        tokens = self.estimate_tokens(text)
        rate = self.cost_per_1k_tokens.get(provider, 0.01)
        return (tokens / 1000) * rate

    # =========================================================
    # PRE-CHECK (BEFORE LLM CALL)
    # =========================================================
    def can_proceed(self, provider: str, text: str) -> Dict[str, Any]:
        tokens = self.estimate_tokens(text)
        cost = self.estimate_cost(provider, text)

        if self.used_tokens + tokens > self.max_tokens:
            return {
                "allowed": False,
                "reason": "Token budget exceeded",
                "tokens": tokens,
                "cost": round(cost, 6),
            }

        if self.used_cost + cost > self.max_cost:
            return {
                "allowed": False,
                "reason": "Cost budget exceeded",
                "tokens": tokens,
                "cost": round(cost, 6),
            }

        return {
            "allowed": True,
            "reason": "OK",
            "tokens": tokens,
            "cost": round(cost, 6),
        }

    # =========================================================
    # UPDATE USAGE (AFTER LLM CALL)
    # =========================================================
    def update(self, provider: str, text: str) -> Dict[str, Any]:
        tokens = self.estimate_tokens(text)
        cost = self.estimate_cost(provider, text)

        self.used_tokens += tokens
        self.used_cost += cost

        return {
            "tokens": tokens,
            "cost": round(cost, 6),
            "total_tokens": self.used_tokens,
            "total_cost": round(self.used_cost, 6),
        }

    # =========================================================
    # SUMMARY (FOR UI / EVENTBUS)
    # =========================================================
    def summary(self) -> Dict[str, Any]:
        return {
            "used_tokens": self.used_tokens,
            "used_cost": round(self.used_cost, 6),
            "max_tokens": self.max_tokens,
            "max_cost": self.max_cost,
        }

    # =========================================================
    # RESET (OPTIONAL PER SESSION)
    # =========================================================
    def reset(self):
        self.used_tokens = 0
        self.used_cost = 0.0
