class CostTracker:
    """
    Simple token + cost estimator (MVP)
    Replace later with provider APIs
    """

    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0

        # rough estimates (update later per provider)
        self.cost_per_1k_tokens = {
            "ollama": 0.0,
            "gemini": 0.0005,
            "openai": 0.01,
            "anthropic": 0.015,
        }

    def estimate_tokens(self, text: str) -> int:
        return len(text.split())  # simple proxy (MVP)

    def add_usage(self, provider: str, text: str):
        tokens = self.estimate_tokens(text)

        cost = (tokens / 1000) * self.cost_per_1k_tokens.get(provider, 0.01)

        self.total_tokens += tokens
        self.total_cost += cost

        return {
            "tokens": tokens,
            "cost": round(cost, 6),
        }

    def summary(self):
        return {
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 6),
        }
