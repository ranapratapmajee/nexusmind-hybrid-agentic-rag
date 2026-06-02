from typing import Any, Dict, List, Optional


class ResultRanker:
    def __init__(self, mode: str = "simple"):
        """
        mode:
        - simple: safe pass-through ranking (MVP)
        - advanced: future ML reranking
        """
        self.mode = mode

    # =========================================================
    # NORMALIZER (CRITICAL FIX)
    # =========================================================
    def _normalize(self, results: Any) -> List[Dict[str, Any]]:
        """
        Converts ANY retriever output into standard format:
        [
            {"text": str, "meta": dict}
        ]
        """

        if not results:
            return []

        normalized = []

        # Case 1: Chroma-style dict
        if isinstance(results, dict):
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])

            # Chroma often returns nested lists
            documents = (
                documents[0]
                if documents and isinstance(documents[0], list)
                else documents
            )
            metadatas = (
                metadatas[0]
                if metadatas and isinstance(metadatas[0], list)
                else metadatas
            )

            for i, doc in enumerate(documents):
                normalized.append(
                    {"text": doc, "meta": metadatas[i] if i < len(metadatas) else {}}
                )

        # Case 2: Already list output (your fallback retriever case)
        elif isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    normalized.append(
                        {
                            "text": item.get("text", ""),
                            "meta": item.get("meta", item.get("metadata", {})),
                        }
                    )
                else:
                    normalized.append({"text": str(item), "meta": {}})

        # Case 3: Unknown format (safety fallback)
        else:
            normalized.append({"text": str(results), "meta": {}})

        return normalized

    # =========================================================
    # SIMPLE RANK (SAFE MVP)
    # =========================================================
    def _simple_rank(self, results: Any) -> List[Dict[str, Any]]:
        normalized = self._normalize(results)

        # no scoring yet → pass-through
        for item in normalized:
            item["score"] = 1.0

        return normalized

    # =========================================================
    # FUTURE ADVANCED RANKING
    # =========================================================
    def _advanced_rank(self, results: Any, query: str):
        ranked = self._simple_rank(results)

        # placeholder scoring
        for item in ranked:
            item["score"] = 1.0

        return sorted(ranked, key=lambda x: x["score"], reverse=True)

    # =========================================================
    # PUBLIC API
    # =========================================================
    def rank(self, results: Any, query: Optional[str] = None):

        if self.mode == "simple":
            return self._simple_rank(results)

        return self._advanced_rank(results, query or "")
