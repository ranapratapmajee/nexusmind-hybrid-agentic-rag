import glob
import hashlib
import os
import re
import time
from typing import Any, Dict, List

import fitz
import ollama

import config
from src.database.operations import VectorStore

# =========================================================
# 🧠 INGESTION PIPELINE (SINGLE FILE, FINAL)
# =========================================================


class IngestionPipeline:
    """
    NexusMind Unified Ingestion System (FINAL)

    RESPONSIBILITIES:
    -------------------
    1. Load documents (txt, md, pdf)
    2. Clean + preprocess text
    3. Semantic chunking
    4. Embedding generation
    5. Vector DB upsert (Chroma)

    NO OTHER PIPELINES EXIST.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.db = VectorStore()
        self.embedding_model = config.EMBEDDING_MODEL

        print("[Ingestion] Unified pipeline initialized")

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
    # PREPROCESS
    # =========================================================
    def _clean(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text.strip()

    # =========================================================
    # SEMANTIC CHUNKING
    # =========================================================
    def _chunk(
        self, text: str, max_chunk_size: int = 1500, hard_cap: int = 2500
    ) -> List[str]:

        paragraphs = text.split("\n\n")

        chunks = []
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # very large paragraph
            if len(para) > hard_cap:
                if current:
                    chunks.append(current.strip())
                    current = ""

                for i in range(0, len(para), max_chunk_size):
                    chunks.append(para[i : i + max_chunk_size])
                continue

            # normal accumulation
            if len(current) + len(para) > max_chunk_size and current:
                chunks.append(current.strip())
                current = para
            else:
                current += ("\n\n" + para) if current else para

        if current:
            chunks.append(current.strip())

        return chunks

    # =========================================================
    # EMBEDDING
    # =========================================================
    def _embed(self, text: str) -> List[float]:
        response = ollama.embeddings(model=self.embedding_model, prompt=text)
        return response["embedding"]

    # =========================================================
    # ID GENERATOR (DETERMINISTIC)
    # =========================================================
    def _generate_id(self, text: str, source: str, idx: int) -> str:
        raw = f"{source}::{idx}::{text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # =========================================================
    # MAIN PIPELINE
    # =========================================================
    def run(self):
        print("\n🚀 Starting Unified Ingestion Pipeline...\n")

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

            ids = []
            texts = []
            embeddings = []
            metadatas = []

            for i, chunk in enumerate(chunks):
                chunk_id = self._generate_id(text=chunk, source=doc["filename"], idx=i)

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

            # SAFE UPSERT (idempotent)
            self.db.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            total_chunks += len(chunks)

        elapsed = time.time() - start_time

        print("\n✅ INGESTION COMPLETE")
        print(f"📊 Total chunks: {total_chunks}")
        print(f"⏱️ Time: {elapsed:.2f}s\n")


# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    IngestionPipeline().run()
