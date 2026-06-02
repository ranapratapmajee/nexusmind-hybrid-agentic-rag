import time

from src.database import VectorStore
from src.pipeline.chunking import semantic_chunk
from src.pipeline.embedder import Embedder
from src.pipeline.loader import LocalFileLoader
from src.pipeline.preprocess import TextPreprocessor
from src.pipeline.utils import generate_id


class IngestionPipeline:
    def __init__(self):
        self.loader = LocalFileLoader()
        self.preprocessor = TextPreprocessor()
        self.embedder = Embedder()
        self.db = VectorStore()

    def run(self):
        print("\n🚀 Starting Ingestion Pipeline...\n")

        documents = self.loader.load()

        if not documents:
            print("⚠️ No documents found")
            return

        total_chunks = 0
        total_start_time = time.time()

        for doc in documents:
            print(f"\n📄 Processing: {doc['filename']}")
            start_time = time.time()

            # Step 1: Clean
            clean_text = self.preprocessor.clean(doc["content"])

            # Step 2: Chunk
            chunks = semantic_chunk(clean_text)
            print(f"✂️  Total chunks: {len(chunks)}")

            ids, docs, embeddings, metadatas = [], [], [], []

            # Step 3: Embed
            for i, chunk in enumerate(chunks, start=1):
                chunk_id = generate_id(
                    text=chunk,
                    source=doc["filename"],
                    chunk_index=i,
                )

                print(f"   🔹 Chunk {i}/{len(chunks)} | len={len(chunk)}")

                embedding = self.embedder.embed(chunk)

                ids.append(chunk_id)
                docs.append(chunk)
                embeddings.append(embedding)
                metadatas.append(
                    {
                        "source": doc["source"],
                        "filename": doc["filename"],
                        "chunk_index": i,
                    }
                )

            # Step 4: SAFE UPSERT (no duplicates ever)
            self.db.upsert(
                ids=ids,
                documents=docs,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            elapsed = time.time() - start_time
            print(f"⏱️  Done in {elapsed:.2f}s")

            total_chunks += len(chunks)

        total_elapsed = time.time() - total_start_time

        print("\n✅ Ingestion Complete")
        print(f"📊 Total chunks processed: {total_chunks}")
        print(f"⏱️  Total time: {total_elapsed:.2f}s\n")


if __name__ == "__main__":
    IngestionPipeline().run()
