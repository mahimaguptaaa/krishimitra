import numpy as np

class Embedder:
    _model = None  # Class-level singleton

    def _get_model(self):
        if Embedder._model is None:
            from sentence_transformers import SentenceTransformer
            Embedder._model = SentenceTransformer("all-MiniLM-L6-v2")
        return Embedder._model

    def embed(self, texts: list) -> np.ndarray:
        return self._get_model().encode(texts, show_progress_bar=False).astype("float32")

    def embed_single(self, text: str) -> np.ndarray:
        return self._get_model().encode([text]).astype("float32")[0]