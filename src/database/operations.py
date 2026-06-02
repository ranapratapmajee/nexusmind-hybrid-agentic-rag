import config
from src.database.chroma import ChromaVectorClient


class VectorStore:
    def __init__(self):
        self.db = ChromaVectorClient()
        self.collection = self.db.get_collection()

    def add(self, ids, documents, embeddings, metadatas=None):
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def upsert(self, ids, documents, embeddings, metadatas=None):
        """
        Safe upsert:
        - deletes existing ids first (if any)
        - then adds fresh values
        """

        try:
            # Chroma supports delete by ids
            self.collection.delete(ids=ids)
        except Exception:
            # ignore if ids don't exist
            pass

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(self, query_embedding, top_k=None):

        top_k = top_k or config.top_k

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

    def delete(self, ids):
        self.collection.delete(ids=ids)
