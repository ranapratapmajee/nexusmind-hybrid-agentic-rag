class ContextManager:
    """
    🧠 NexusMind Context Fusion Engine (FINAL VERSION)

    Responsibility:
    ONLY builds structured LLM input from different sources.

    It does NOT:
    - store memory
    - retrieve memory
    - run models
    - execute tools
    """

    # =========================================================
    # COMPRESSION (SAFE + LIGHTWEIGHT)
    # =========================================================
    def compress(self, items: list[str], max_items: int = 6) -> str:
        if not items:
            return ""

        cleaned = [i.strip() for i in items if i and i.strip()]
        return "\n\n".join(cleaned[-max_items:])

    # =========================================================
    # TOKEN ESTIMATOR (LIGHTWEIGHT APPROX)
    # =========================================================
    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4 if text else 0

    # =========================================================
    # SAFE TRIM (CRITICAL FOR LONG CONTEXTS)
    # =========================================================
    def _trim(self, text: str, max_tokens: int) -> str:
        if not text:
            return ""

        if self._estimate_tokens(text) <= max_tokens:
            return text.strip()

        char_limit = max_tokens * 4
        return text[-char_limit:].strip()

    # =========================================================
    # MAIN CONTEXT BUILDER (CORE FUNCTION)
    # =========================================================
    def build(
        self,
        memory: str = "",
        rag: str = "",
        tool: str = "",
        system: str = "",
        max_tokens: int = 1200,
    ) -> str:

        # -------------------------
        # PRIORITY TRIMMING
        # -------------------------
        system = self._trim(system, max_tokens // 4)
        tool = self._trim(tool, max_tokens // 4)
        rag = self._trim(rag, max_tokens // 3)
        memory = self._trim(memory, max_tokens // 2)

        sections = []

        # -------------------------
        # SYSTEM (HIGHEST PRIORITY)
        # -------------------------
        if system:
            sections.append("### SYSTEM (HIGH PRIORITY)\n" + system)

        # -------------------------
        # TOOL OUTPUT (GROUND TRUTH)
        # -------------------------
        if tool:
            sections.append("### TOOL OUTPUT\n" + tool)

        # -------------------------
        # RAG CONTEXT
        # -------------------------
        if rag:
            sections.append("### KNOWLEDGE BASE\n" + rag)

        # -------------------------
        # MEMORY (CONVERSATION)
        # -------------------------
        if memory:
            sections.append("### MEMORY\n" + memory)

        return "\n\n".join(sections).strip()
