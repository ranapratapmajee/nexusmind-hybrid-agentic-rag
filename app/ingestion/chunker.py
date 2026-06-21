# app/ingestion/chunker.py

from typing import List, Dict, Any
from config.settings import get_settings

class SemanticChunker:
    def __init__(self):
        self.settings = get_settings()
        self.chunk_size = self.settings.rag.chunk_size
        self.chunk_overlap = self.settings.rag.chunk_overlap

    def split_text(self, text: str, source_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Splits raw text strings into fixed-size semantic windows with a calculated overlap.
        Preserves contextual metadata references for perfect upstream vector/graph attribution.
        """
        if not text:
            return []

        # Token-approximate splitting by whitespace boundaries (production baseline)
        words = text.split()
        chunks = []
        meta = source_metadata or {}
        
        stride = self.chunk_size - self.chunk_overlap
        if stride <= 0:
            stride = self.chunk_size // 2

        for i in range(0, len(words), stride):
            word_window = words[i : i + self.chunk_size]
            chunk_text = " ".join(word_window)
            
            # Prevent lingering micro-chunks at the extreme tail of the document
            if len(word_window) < 10 and chunks:
                break
                
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **meta,
                    "chunk_index": len(chunks),
                    "word_count": len(word_window)
                }
            })
            
            if i + self.chunk_size >= len(words):
                break
                
        return chunks