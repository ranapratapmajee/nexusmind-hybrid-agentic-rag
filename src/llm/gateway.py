from typing import Any, Dict, Generator, Optional

import config


# =========================================================
# 🧠 LLM GATEWAY (MULTI-MODEL CONTROL TOWER)
# =========================================================
class LLMGateway:
    """
    NexusMind Central Intelligence Router

    Responsibilities:
    - Model selection (AUTO MODE)
    - Fallback handling
    - Streaming + non-streaming API
    - Unified interface for ALL LLMs
    """

    def __init__(self):
        print("[LLM Gateway] Initializing multi-model engine...")

        # -------------------------
        # MODEL ORDER (HARD RULE)
        # -------------------------
        self.model_chain = [
            "ollama",
            "gemini",
            "openai",
            "anthropic",
        ]

        # -------------------------
        # CONFIG
        # -------------------------
        self.temperature = config.TEMPERATURE

        # Lazy imports (avoid startup cost)
        self._clients = {}

        print("[LLM Gateway] Ready with AUTO fallback chain.")

    # =========================================================
    # MODEL SELECTOR (INTELLIGENT ROUTING)
    # =========================================================
    def select_model(self, route: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """
        Decide best model based on task complexity.
        """

        action = route.get("action", "DIRECT_ANSWER")

        # -------------------------
        # LOCAL FIRST (DEFAULT)
        # -------------------------
        if action in ["DIRECT_ANSWER", "RAG_SEARCH", "EXECUTE_TOOL"]:
            return "ollama"

        # -------------------------
        # WEB / HYBRID → better reasoning
        # -------------------------
        if action in ["WEB_SEARCH", "HYBRID"]:
            return "gemini"

        return "ollama"

    # =========================================================
    # CORE GENERATION ENTRY
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

            except Exception as e:
                print(f"[Gateway] {provider} failed: {e}")
                continue

        return "[Gateway Error] All models failed."

    # =========================================================
    # STREAMING ENTRY
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

        try:
            yield from self._stream_model(model, query, context)

        except Exception as e:
            yield f"[Gateway Stream Error] {str(e)}"

    # =========================================================
    # INTERNAL MODEL CALL (SYNC)
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
            # Lazy import placeholder
            return self._mock("Gemini", query, context)

        elif provider == "openai":
            return self._mock("OpenAI", query, context)

        elif provider == "anthropic":
            return self._mock("Anthropic", query, context)

        raise Exception(f"Unknown provider: {provider}")

    # =========================================================
    # STREAM MODEL CALL
    # =========================================================
    def _stream_model(self, provider: str, query: str, context: str):

        if provider == "ollama":
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

        else:
            # fallback streaming simulation
            text = self._call_model(provider, query, context)
            for w in text.split():
                yield w + " "

    # =========================================================
    # INPUT BUILDER
    # =========================================================
    def _build_input(self, query: str, context: str) -> str:
        if context:
            return f"QUERY:\n{query}\n\nCONTEXT:\n{context}"
        return query

    # =========================================================
    # SYSTEM PROMPT (GLOBAL CONTROL)
    # =========================================================
    def _system_prompt(self) -> str:
        return f"""
You are {config.ASSISTANT_NAME}, an intelligent AI inside NexusMind.

RULES:
- Be accurate and concise
- Use context if provided
- Prefer structured answers when needed
- Do not hallucinate
"""

    # =========================================================
    # MOCK FALLBACK (TEMPORARY)
    # =========================================================
    def _mock(self, provider: str, query: str, context: str) -> str:
        return f"[{provider} MOCK RESPONSE] {query}"
