import faiss
import numpy as np
import pickle
from pathlib import Path
from config import settings

class FAISSStore:
    DIM = 384  # all-MiniLM-L6-v2 dimension

    def __init__(self):
        self.index_path = Path(settings.FAISS_DIR) / "faiss.index"
        self.meta_path  = Path(settings.FAISS_DIR) / "faiss_meta.pkl"
        Path(settings.FAISS_DIR).mkdir(exist_ok=True)
        self.index    = self._load_index()
        self.metadata = self._load_meta()

    def _load_index(self):
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        return faiss.IndexFlatIP(self.DIM)  # Inner Product on normalized = cosine similarity

    def _load_meta(self):
        if self.meta_path.exists():
            return pickle.loads(self.meta_path.read_bytes())
        return []

    def _save(self):
        faiss.write_index(self.index, str(self.index_path))
        self.meta_path.write_bytes(pickle.dumps(self.metadata))

    def add(self, embeddings: np.ndarray, metadata: list):
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.metadata.extend(metadata)
        self._save()

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> list:
        if self.index.ntotal == 0:
            return []
        q = query_vec.reshape(1, -1).astype("float32")
        faiss.normalize_L2(q)
        scores, indices = self.index.search(q, min(top_k, self.index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append({**self.metadata[idx], "score": float(score)})
        return results

    def total_chunks(self) -> int:
        return self.index.ntotal
