import json
from typing import Dict, List

import config


# =========================================================
# 🧠 PLANNER ENGINE (CLEAN EVENTBUS VERSION)
# =========================================================
class Planner:
    """
    NexusMind Planning Engine

    ROLE:
    - Convert query → execution tasks
    - NO routing logic (router handles that)
    - NO reasoning leakage
    - PURE structured output
    """

    def __init__(self):
        print("[Planner] Initialized (EventBus-safe)")

    # =========================================================
    # RULE-BASED PLANNING (FAST PATH)
    # =========================================================
    def _rule_based_plan(self, query: str) -> List[str]:
        q = query.lower().strip()

        tasks = []

        # MEMORY
        if any(k in q for k in ["my name", "remember", "who am i", "what did i"]):
            tasks.append("MEMORY")

        # TOOLS
        if any(k in q for k in ["calculate", "+", "-", "*", "/", "solve"]):
            tasks.append("USE_TOOLS")

        # RAG
        if any(
            k in q
            for k in ["explain", "what is", "how does", "architecture", "rag", "vector"]
        ):
            tasks.append("RAG_SEARCH")

        # DEFAULT
        if not tasks:
            tasks.append("DIRECT")

        return tasks

    # =========================================================
    # MAIN ENTRY
    # =========================================================
    def create_plan(self, query: str, memory_context: str = "") -> Dict:
        """
        Returns:
        {
            "tasks": [...],
        }
        """

        # -------------------------------------------------
        # 1. FAST RULE-BASED PLAN
        # -------------------------------------------------
        tasks = self._rule_based_plan(query)

        # -------------------------------------------------
        # 2. SIMPLE QUERIES → RETURN IMMEDIATELY
        # -------------------------------------------------
        if len(tasks) <= 2:
            return {"tasks": tasks}

        # -------------------------------------------------
        # 3. OPTIONAL LLM ENHANCEMENT
        # -------------------------------------------------
        try:
            import ollama

            system_prompt = """
You are a planning engine.

Convert query into minimal execution tasks.

Allowed:
- RAG_SEARCH
- USE_TOOLS
- MEMORY
- DIRECT

Return JSON ONLY:
{
  "tasks": [...]
}
"""

            response = ollama.chat(
                model=config.ROUTER_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"QUERY: {query}\nMEMORY:\n{memory_context}",
                    },
                ],
                format={
                    "type": "object",
                    "properties": {
                        "tasks": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["tasks"],
                },
                options={"temperature": 0.2},
            )

            result = json.loads(response["message"]["content"])

            return {
                "tasks": result.get("tasks", tasks),
            }

        except Exception:
            # SAFE FALLBACK
            return {"tasks": tasks}
