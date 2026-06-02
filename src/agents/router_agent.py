import json
from typing import Literal, Optional

import ollama
from pydantic import Field, create_model

import config

# ----------------------------
# 1. ROUTING SPACE
# ----------------------------
AVAILABLE_AGENTS = {
    "DIRECT_ANSWER": "Casual chat, greetings, general knowledge",
    "RAG_SEARCH": "Knowledge base / documents / technical queries",
    "EXECUTE_TOOL": "Math, calculations, structured tool usage",
}

# FIX: proper Literal creation
agent_keys = list(AVAILABLE_AGENTS.keys())
DynamicActionType = Literal["DIRECT_ANSWER", "RAG_SEARCH", "EXECUTE_TOOL"]

# ----------------------------
# 2. TOOL ROUTING EXTENSION
# ----------------------------
ToolType = Literal["calculator", "web_search", "none"]

# ----------------------------
# 3. ROUTER SCHEMA
# ----------------------------
RouterSchema = create_model(
    "RouterSchema",
    action=(DynamicActionType, Field(description="Final routing decision")),
    tool=(
        Optional[ToolType],
        Field(description="If EXECUTE_TOOL, specify tool name else null"),
    ),
    optimized_query=(
        str,
        Field(description="Compressed query for RAG retrieval (keywords only)"),
    ),
    confidence=(float, Field(description="Confidence score between 0 and 1")),
    reasoning=(str, Field(description="Brief explanation of routing decision")),
)


# ----------------------------
# 4. ROUTER AGENT
# ----------------------------
class RouterAgent:
    def __init__(self):
        # FIX: correct settings field
        self.model = config.ROUTER_MODEL
        print(f"[Router] Initialized with model: {self.model}")

    def route(self, user_prompt: str) -> dict:
        system_prompt = f"""
You are the routing brain of Nexa.

You MUST classify every query into EXACTLY one of:

- DIRECT_ANSWER → casual chat, greetings, general knowledge
- RAG_SEARCH → documents, PDFs, files, knowledge base, vector DB, or unclear queries
- EXECUTE_TOOL → math, calculations, coding, structured execution

RULES:
- If unsure → ALWAYS choose RAG_SEARCH
- If query contains doc/file/pdf/dataset/notes/context → RAG_SEARCH
- If math/calculation → EXECUTE_TOOL

Available Paths:
{chr(10).join([f"- {k}: {v}" for k, v in AVAILABLE_AGENTS.items()])}

Return strict JSON only.
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                format=RouterSchema.model_json_schema(),
                options={"temperature": config.LLM_TEMPERATURE},
            )

            result = json.loads(response["message"]["content"])

            # safety normalization
            if result.get("action") != "EXECUTE_TOOL":
                result["tool"] = None

            return result

        except Exception as e:
            return {
                "action": "DIRECT_ANSWER",
                "tool": None,
                "optimized_query": user_prompt,
                "confidence": 0.3,
                "reasoning": f"fallback due to error: {str(e)}",
            }
