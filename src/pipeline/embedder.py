import ollama

import config


class Embedder:
    """
    Local embedding using Ollama (nomic-embed-text)
    """

    def __init__(self):
        self.model = config.EMBEDDING_MODEL

    def embed(self, text: str):
        response = ollama.embed(model=self.model, input=text)
        return response["embeddings"][0]
