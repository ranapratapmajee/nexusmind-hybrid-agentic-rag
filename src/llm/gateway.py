from typing import Any, Dict, Generator, Optional

import config


# =========================================================
# 🧠 LLM GATEWAY (PURE MODEL ENGINE)
# =========================================================
class LLMGateway:
    """
    NexusMind Central Intelligence Router

    RULE:
    - PURE LLM ENGINE ONLY
    - NO EVENTBUS
    - NO STREAM FORMATTING
    - NO ORCHESTRATION LOGIC
    """

    def __init__(self):
        self.model_chain = [
            "ollama",
            "gemini",
            "openai",
            "anthropic",
        ]

        self.temperature = config.TEMPERATURE

    # =========================================================
    def select_model(self, route: Dict[str, Any], plan: Dict[str, Any]) -> str:

        action = route.get("action", "DIRECT_ANSWER")

        if action in ["DIRECT_ANSWER", "RAG_SEARCH", "EXECUTE_TOOL"]:
            return "ollama"

        if action in ["WEB_SEARCH", "HYBRID"]:
            return "gemini"

        return "ollama"

    # =========================================================
    def generate(
        self,
        query: str,
        context: str = "",
        route: Optional[Dict] = None,
        plan: Optional[Dict] = None,
    ) -> str:

        route = route or {}
        plan = plan or {}

        model = self.select_model(route, plan)

        for provider in self.model_chain:
            try:
                if provider == model:
                    return self._call_model(provider, query, context)

            except Exception:
                continue

        raise Exception("All models failed")

    # =========================================================
    def stream(
        self,
        query: str,
        context: str = "",
        route: Optional[Dict] = None,
        plan: Optional[Dict] = None,
    ) -> Generator[str, None, None]:

        route = route or {}
        plan = plan or {}

        model = self.select_model(route, plan)

        # direct streaming
        if model == "ollama":
            import ollama

            stream = ollama.chat(
                model=config.ROUTER_MODEL,
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": self._build_input(query, context)},
                ],
                stream=True,
                options={"temperature": self.temperature},
            )

            for chunk in stream:
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token
            return

        # fallback streaming
        text = self._call_model(model, query, context)
        for word in text.split():
            yield word + " "

    # =========================================================
    def _call_model(self, provider: str, query: str, context: str) -> str:

        if provider == "ollama":
            import ollama

            response = ollama.chat(
                model=config.ROUTER_MODEL,
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": self._build_input(query, context)},
                ],
                options={"temperature": self.temperature},
            )

            return response["message"]["content"]

        elif provider == "gemini":
            return self._mock("Gemini", query)

        elif provider == "openai":
            return self._mock("OpenAI", query)

        elif provider == "anthropic":
            return self._mock("Anthropic", query)

        raise Exception(f"Unknown provider: {provider}")

    # =========================================================
    def _build_input(self, query: str, context: str) -> str:
        if context:
            return f"QUERY:\n{query}\n\nCONTEXT:\n{context}"
        return query

    # =========================================================
    def _system_prompt(self) -> str:
        return f"""
You are {config.ASSISTANT_NAME}.

RULES:
- Be accurate and concise
- Use context if provided
- Do not hallucinate
"""

    # =========================================================
    def _mock(self, provider: str, query: str) -> str:
        return f"[{provider} MOCK RESPONSE] {query}"
