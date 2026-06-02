from typing import Dict, List

import config


class TaskPlan:
    def __init__(self, tasks: List[str], reasoning: str):
        self.tasks = tasks
        self.reasoning = reasoning

    def dict(self):
        return {
            "tasks": self.tasks,
            "reasoning": self.reasoning,
        }


class Planner:
    """
    🧠 Lightweight Planning Engine (FINAL VERSION)

    ROLE:
    - Break query into execution steps
    - DOES NOT decide routing (Router handles that)
    - MUST be fast, cheap, deterministic first
    """

    def __init__(self):
        print("[Planner] Initialized (Deterministic + Hybrid Mode)")

    # =========================================================
    # FAST RULE-BASED PLANNING (NO LLM - DEFAULT PATH)
    # =========================================================
    def _rule_based_plan(self, query: str) -> TaskPlan:
        q = query.lower()

        tasks = []

        # MEMORY always helpful for conversational queries
        if any(k in q for k in ["my name", "remember", "who am i", "what did i"]):
            tasks.append("MEMORY")

        # TOOL hints (but router decides final execution)
        if any(k in q for k in ["calculate", "+", "-", "*", "/", "solve"]):
            tasks.append("USE_TOOLS")

        # RAG hints
        if any(
            k in q
            for k in ["explain", "what is", "how does", "architecture", "rag", "vector"]
        ):
            tasks.append("RAG_SEARCH")

        # default fallback
        if not tasks:
            tasks.append("DIRECT")

        return TaskPlan(
            tasks=tasks,
            reasoning="rule-based planning (fast path)",
        )

    # =========================================================
    # MAIN PLANNING ENTRY
    # =========================================================
    def create_plan(self, query: str, memory_context: str = "") -> Dict:
        """
        Hybrid strategy:
        1. Rule-based first (FAST + FREE)
        2. LLM only if complexity detected
        """

        # STEP 1: FAST PATH
        rule_plan = self._rule_based_plan(query)

        # If simple → return immediately (NO LLM COST)
        if len(rule_plan.tasks) <= 2:
            return rule_plan.dict()

        # STEP 2: OPTIONAL LLM ENHANCEMENT (ONLY FOR COMPLEX QUERIES)
        try:
            import ollama

            system_prompt = """
You are an advanced planning engine.

Convert user query into minimal execution steps.

Allowed tasks:
- RAG_SEARCH
- USE_TOOLS
- MEMORY
- DIRECT

Return JSON only:
{
  "tasks": [...],
  "reasoning": "short explanation"
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
                        "tasks": {"type": "array", "items": {"type": "string"}},
                        "reasoning": {"type": "string"},
                    },
                    "required": ["tasks", "reasoning"],
                },
                options={"temperature": 0.2},
            )

            import json

            result = json.loads(response["message"]["content"])

            return TaskPlan(
                tasks=result.get("tasks", rule_plan.tasks),
                reasoning=result.get("reasoning", "llm-enhanced planning"),
            ).dict()

        except Exception:
            # SAFE FALLBACK (NEVER FAIL SYSTEM)
            return rule_plan.dict()
