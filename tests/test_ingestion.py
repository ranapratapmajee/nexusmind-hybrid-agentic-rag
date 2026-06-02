import os
import sys

sys.path.append(os.path.abspath("."))

from config import RAG_EMBEDDING_DIMENSION
from src.database.operations import VectorStore
from src.intelligence.rag import RAG


# =========================================================
# 🧪 VECTOR STORE DIRECT TEST
# =========================================================
def test_vectorstore_direct():
    print("\n🧪 VECTOR STORE CHECK")

    db = VectorStore()

    # FIX: match embedding dimension from config
    dummy_embedding = [0.01] * RAG_EMBEDDING_DIMENSION

    results = db.query(query_embedding=dummy_embedding, top_k=3)

    print("✔ Raw results:", results)


# =========================================================
# 🧪 RAG PIPELINE TEST
# =========================================================
def test_rag_pipeline():
    print("\n🧪 RAG PIPELINE CHECK")

    rag = RAG()

    result = rag.retrieve("machine learning", top_k=3)

    print("✔ Context:\n", result.get("context", ""))


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    test_vectorstore_direct()
    test_rag_pipeline()
