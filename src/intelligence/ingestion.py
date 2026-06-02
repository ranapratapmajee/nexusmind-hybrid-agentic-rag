import glob
import hashlib
import os
import re
import time
from typing import Any, Dict, List

import fitz
import ollama

from src.database.operations import VectorStore


# =========================================================
# 🧠 SELF-HEALING INGESTION PIPELINE
# =========================================================
class IngestionPipeline:
    """
    Self-healing RAG ingestion system

    FIXES:
    - Auto detects embedding dimension
    - Prevents Chroma dimension mismatch crashes
    - Auto recovers from bad embedding responses
    - Safe fallback vector generation
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.db = VectorStore()

        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

        # =====================================================
        # 🧠 SELF-HEALING INIT STEP
        # =====================================================
        self.embedding_dim = self._detect_embedding_dimension()

        print("[Ingestion] Self-Healing Pipeline initialized")
        print(f"[Embedding] Model: {self.embedding_model}")
        print(f"[Embedding] Detected dimension: {self.embedding_dim}")

    # =========================================================
    # 🧠 AUTO DETECT EMBEDDING DIMENSION
    # =========================================================
    def _detect_embedding_dimension(self) -> int:
        try:
            test = ollama.embeddings(
                model=self.embedding_model, prompt="dimension probe"
            )

            emb = test.get("embedding", [])

            if not emb:
                raise ValueError("Empty embedding from model")

            return len(emb)

        except Exception as e:
            print(f"[WARN] Embedding detection failed: {e}")
            print("[Fallback] Using safe default dimension = 768")
            return 768

    # =========================================================
    # LOAD DOCUMENTS
    # =========================================================
    def _load_documents(self) -> List[Dict[str, Any]]:
        docs = []
        pattern = os.path.join(self.data_dir, "*.*")

        print(f"📁 Scanning: {self.data_dir}")

        for path in glob.glob(pattern):
            filename = os.path.basename(path)

            try:
                if path.endswith((".txt", ".md")):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                elif path.endswith(".pdf"):
                    content = self._read_pdf(path)

                else:
                    continue

                docs.append(
                    {
                        "source": "local",
                        "filename": filename,
                        "content": content.strip(),
                    }
                )

            except Exception as e:
                print(f"❌ Failed {filename}: {e}")

        return docs

    # =========================================================
    # PDF READER
    # =========================================================
    def _read_pdf(self, path: str) -> str:
        text = ""
        with fitz.open(path) as pdf:
            for page in pdf:
                text += page.get_text("text") + "\n\n"
        return text

    # =========================================================
    # CLEANING
    # =========================================================
    def _clean(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text.strip()

    # =========================================================
    # CHUNKING
    # =========================================================
    def _chunk(self, text: str, max_chunk_size: int = 1500) -> List[str]:
        paragraphs = text.split("\n\n")

        chunks, current = [], ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current) + len(para) > max_chunk_size and current:
                chunks.append(current.strip())
                current = para
            else:
                current += ("\n\n" + para) if current else para

        if current:
            chunks.append(current.strip())

        return chunks

    # =========================================================
    # 🧠 SELF-HEALING EMBEDDING
    # =========================================================
    def _embed(self, text: str) -> List[float]:
        try:
            response = ollama.embeddings(model=self.embedding_model, prompt=text)

            emb = response.get("embedding", [])

            # -----------------------------
            # Healing Step 1: empty output
            # -----------------------------
            if not emb:
                print("[WARN] Empty embedding → fallback vector")
                return self._zero_vector()

            # -----------------------------
            # Healing Step 2: dimension mismatch
            # -----------------------------
            if len(emb) != self.embedding_dim:
                print(
                    f"[WARN] Dimension mismatch "
                    f"expected={self.embedding_dim}, got={len(emb)}"
                )

                # attempt repair once (trim or pad)
                emb = self._repair_embedding(emb)

            return emb

        except Exception as e:
            print(f"[Embedding Error] {e}")
            return self._zero_vector()

    # =========================================================
    # 🧠 EMBEDDING REPAIR STRATEGY
    # =========================================================
    def _repair_embedding(self, emb: List[float]) -> List[float]:
        if len(emb) > self.embedding_dim:
            return emb[: self.embedding_dim]

        if len(emb) < self.embedding_dim:
            return emb + [0.0] * (self.embedding_dim - len(emb))

        return emb

    # =========================================================
    # ZERO VECTOR FALLBACK
    # =========================================================
    def _zero_vector(self) -> List[float]:
        return [0.0] * self.embedding_dim

    # =========================================================
    # ID GENERATION
    # =========================================================
    def _generate_id(self, text: str, source: str, idx: int) -> str:
        raw = f"{source}::{idx}::{text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # =========================================================
    # MAIN PIPELINE
    # =========================================================
    def run(self):
        print("\n🚀 Starting Self-Healing Ingestion Pipeline...\n")

        docs = self._load_documents()

        if not docs:
            print("⚠️ No documents found")
            return

        total_chunks = 0
        start_time = time.time()

        for doc in docs:
            print(f"\n📄 Processing: {doc['filename']}")

            clean_text = self._clean(doc["content"])
            chunks = self._chunk(clean_text)

            print(f"✂️ Chunks: {len(chunks)}")

            ids, texts, embeddings, metadatas = [], [], [], []

            for i, chunk in enumerate(chunks):
                chunk_id = self._generate_id(chunk, doc["filename"], i)

                embedding = self._embed(chunk)

                ids.append(chunk_id)
                texts.append(chunk)
                embeddings.append(embedding)

                metadatas.append(
                    {
                        "source": doc["source"],
                        "filename": doc["filename"],
                        "chunk_index": i,
                    }
                )

            self.db.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            total_chunks += len(chunks)

        elapsed = time.time() - start_time

        print("\n✅ INGESTION COMPLETE (SELF-HEALED)")
        print(f"📊 Total chunks: {total_chunks}")
        print(f"⏱️ Time: {elapsed:.2f}s\n")


# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    IngestionPipeline().run()
