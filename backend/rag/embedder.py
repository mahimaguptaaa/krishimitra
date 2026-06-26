import numpy as np
from config import settings

class Embedder:
    def embed(self, texts: list) -> np.ndarray:
        return np.array([self._embed_one(t) for t in texts], dtype="float32")

    def embed_single(self, text: str) -> np.ndarray:
        return self._embed_one(text)

    def _embed_one(self, text: str) -> np.ndarray:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
        )
        return np.array(result["embedding"], dtype="float32")