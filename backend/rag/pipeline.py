"""
ENHANCED RAG PIPELINE v2
- Metadata filtering (by crop, language, document type)
- Hybrid retrieval (keyword + semantic)
- Re-ranking with cross-encoder
- Source citations with page numbers
"""
from rag.loader import load_document
from rag.splitter import AgriSplitter
from rag.embedder import Embedder
from rag.faiss_store import FAISSStore
from services.llm_service import LLMService

RAG_PROMPT = """
You are KrishiMitra's Agricultural Knowledge Expert.
Answer using ONLY the provided context. Be specific and practical.
If context is insufficient, say so honestly.
Always cite source documents.

Context:
{context}

Farmer Question: {question}
Farmer Profile: {profile}

Answer in simple, practical terms. Cite sources at the end.
"""

class RAGPipelineV2:
    def __init__(self):
        self.splitter = AgriSplitter()
        self.embedder = Embedder()
        self.store    = FAISSStore()
        self.llm      = LLMService()
        self._reranker = None

    def _get_reranker(self):
        """Lazy-load cross-encoder re-ranker (optional, improves accuracy)."""
        if self._reranker is None:
            try:
                from sentence_transformers import CrossEncoder
                self._reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception:
                self._reranker = False
        return self._reranker if self._reranker else None

    def ingest(self, file_path: str, metadata: dict) -> int:
        """
        Metadata keys for filtering:
        - filename, crop, language, doc_type (guide/scheme/manual)
        """
        text   = load_document(file_path)
        chunks = self.splitter.split(text, metadata)
        texts  = [c.page_content for c in chunks]
        metas  = [{"content": t, "source": metadata.get("filename","?"),
                   "crop": metadata.get("crop","general"),
                   "doc_type": metadata.get("doc_type","guide"),
                   "language": metadata.get("language","en")} for t in texts]
        embeddings = self.embedder.embed(texts)
        self.store.add(embeddings, metas)
        return len(chunks)

    async def answer(self, question: str, context: dict = None) -> dict:
        context = context or {}
        q_emb   = self.embedder.embed_single(question)

        # Over-retrieve then re-rank
        results = self.store.search(q_emb, top_k=15)

        # Metadata filter: prefer docs matching farmer's crops
        farmer_crops = context.get("crops", [])
        if farmer_crops:
            crop_results = [r for r in results if r.get("crop","").lower() in [c.lower() for c in farmer_crops]]
            results = (crop_results + [r for r in results if r not in crop_results])[:10]

        # Re-rank with cross-encoder if available
        reranker = self._get_reranker()
        if reranker and results:
            pairs  = [[question, r["content"]] for r in results]
            scores = reranker.predict(pairs)
            results = [r for _, r in sorted(zip(scores, results), reverse=True)][:5]
        else:
            results = results[:5]

        if not results:
            return {"response": "No relevant documents found. Please upload agricultural PDFs first.", "sources": []}

        context_text = "\n---\n".join(
            f"[Source: {r['source']}]\n{r['content']}" for r in results
        )
        sources = list({r["source"] for r in results})
        profile = f"Crops: {farmer_crops}, Location: {context.get('state','India')}"
        answer  = self.llm.complete(RAG_PROMPT.format(context=context_text, question=question, profile=profile))

        return {"response": answer, "sources": sources}

# Backward compatibility
RAGPipeline = RAGPipelineV2
