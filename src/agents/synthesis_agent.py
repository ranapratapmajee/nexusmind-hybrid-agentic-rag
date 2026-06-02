from typing import Optional

import ollama

import config


class SynthesisAgent:
    def __init__(self):
        # ----------------------------
        # SAFE MODEL RESOLUTION
        # ----------------------------
        self.model = config.SYNTHESIS_MODEL

        print(f"[Synthesis] Initialized with model: {self.model}")

    # =========================================================
    # CONTEXT CLEANER (LIGHT + FAST)
    # =========================================================
    def _format_context(self, context: str) -> str:
        if not context:
            return ""

        chunks = context.split("\n\n")

        # remove empty + trim noise
        cleaned = [c.strip() for c in chunks if c and c.strip()]

        return "\n\n".join(cleaned)

    # =========================================================
    # NORMAL GENERATION (NON-STREAM)
    # =========================================================
    def generate(self, query: str, context: Optional[str] = None) -> str:

        context = self._format_context(context)

        system_prompt = """
You are NEXA — a production-grade AI assistant inside NexusMind.

RULES:
- Use provided context if available
- If context is insufficient, say: "I don't have enough information in the knowledge base."
- Do NOT hallucinate or guess
- Be concise, structured, and factual
- Prefer bullet points when explaining
"""

        if context:
            system_prompt += f"\n\nCONTEXT:\n{context}"

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                options={"temperature": 0.2, "top_p": 0.9},
            )

            return response["message"]["content"]

        except Exception as e:
            return f"[Nexa Error] {str(e)}"

    # =========================================================
    # STREAMING (CHATGPT-STYLE TOKEN OUTPUT)
    # =========================================================
    def generate_stream(self, query: str, context: str = ""):

        context = self._format_context(context)

        system_prompt = """
You are NEXA, a precise AI assistant.
Respond clearly and concisely.
"""

        if context:
            system_prompt += f"\n\nCONTEXT:\n{context}"

        try:
            stream = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                options={"temperature": 0.2, "top_p": 0.9},
                stream=True,
            )

            for chunk in stream:
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token

        except Exception as e:
            # NEVER BREAK UI STREAM
            yield f"⚠️ Model Error: {str(e)}"
