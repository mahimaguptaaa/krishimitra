from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self):
        # Downloads automatically on first run (~90MB)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts: list) -> np.ndarray:
        return self.model.encode(texts, show_progress_bar=False).astype("float32")

    def embed_single(self, text: str) -> np.ndarray:
        return self.model.encode([text]).astype("float32")[0]
