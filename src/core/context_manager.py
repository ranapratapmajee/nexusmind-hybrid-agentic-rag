class ContextManager:
    """
    Production-grade Context Fusion Engine for Nexa v4.
    Handles safe token compression + structured LLM input.
    """

    # =========================================================
    # SAFE LIST COMPRESSION
    # =========================================================
    def compress(self, items: list[str], max_items: int = 6) -> str:
        if not items:
            return ""

        cleaned = [i.strip() for i in items if i and i.strip()]
        return "\n\n".join(cleaned[-max_items:])

    # =========================================================
    # TOKEN ESTIMATOR
    # =========================================================
    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4 if text else 0

    # =========================================================
    # SAFE TRIM (RECENCY PRIORITY)
    # =========================================================
    def _trim_to_budget(self, text: str, max_tokens: int) -> str:
        if not text:
            return ""

        if self._estimate_tokens(text) <= max_tokens:
            return text.strip()

        char_limit = max_tokens * 4
        return text[-char_limit:].strip()

    # =========================================================
    # CONTEXT BUILDER (CORE FUSION ENGINE)
    # =========================================================
    def build(
        self,
        memory: str = "",
        rag: str = "",
        tool: str = "",
        history: str = "",
        system_memory: str = "",
        max_tokens: int = 1200,
    ) -> str:
        """
        Priority Order:

        1. SYSTEM MEMORY (identity / facts)  ⭐ NEW STRONG LAYER
        2. TOOL OUTPUT (ground truth execution)
        3. RAG CONTEXT (external knowledge)
        4. CHAT HISTORY (conversation continuity)
        5. LONG MEMORY (soft signals if any inside memory)
        """

        # ----------------------------
        # SAFE TRIMMING
        # ----------------------------
        system_memory = self._trim_to_budget(system_memory, max_tokens // 4)
        tool = self._trim_to_budget(tool, max_tokens // 4)
        rag = self._trim_to_budget(rag, max_tokens // 3)
        history = self._trim_to_budget(history, max_tokens // 3)
        memory = self._trim_to_budget(memory, max_tokens // 4)

        sections = []

        # ----------------------------
        # SYSTEM MEMORY (HIGHEST PRIORITY)
        # ----------------------------
        if system_memory:
            sections.append(
                "### SYSTEM MEMORY (HIGHEST PRIORITY - FACTS)\n" + system_memory.strip()
            )

        # ----------------------------
        # TOOL OUTPUT
        # ----------------------------
        if tool:
            sections.append("### TOOL OUTPUT\n" + tool.strip())

        # ----------------------------
        # RAG CONTEXT
        # ----------------------------
        if rag:
            sections.append("### KNOWLEDGE BASE (RAG)\n" + rag.strip())

        # ----------------------------
        # CHAT HISTORY
        # ----------------------------
        if history:
            sections.append("### CONVERSATION HISTORY\n" + history.strip())

        # ----------------------------
        # LONG MEMORY (FALLBACK SIGNALS)
        # ----------------------------
        if memory:
            sections.append("### LONG TERM MEMORY\n" + memory.strip())

        return "\n\n".join(sections).strip()
