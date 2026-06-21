# app/ingestion/vector_ingestor.py

import uuid
from typing import List, Dict, Any
from app.services.chroma_service import ChromaService
from config.settings import get_settings

class VectorIngestor:
    def __init__(self, chroma_service: ChromaService):
        """
        Initialized with ChromaService. 
        EmbeddingService is no longer needed here as Chroma handles vectorization natively.
        """
        self.chroma = chroma_service
        self.settings = get_settings()

    def ingest_document_chunks(self, chunks: List[Dict[str, Any]], filename: str) -> int:
        """
        Batches and injects structured text windows into ChromaDB.
        Delegates vector calculation entirely to Chroma's native Ollama hook.
        """
        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            unique_id = f"{filename}_ch_{chunk['metadata']['chunk_index']}_{uuid.uuid4().hex[:6]}"
            
            ids.append(unique_id)
            documents.append(chunk["text"])
            
            # Protect state boundaries using a clean shallow copy to isolate mutations
            chunk_meta = chunk["metadata"].copy()
            chunk_meta["source_file"] = filename
            metadatas.append(chunk_meta)

        # Pass text directly. ChromaDB automatically batches and calls Ollama for embeddings.
        self.chroma.add_chunks(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=None  # Triggers automatic local 'nomic-embed-text' generation
        )
        
        return len(ids)
