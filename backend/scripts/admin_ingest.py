"""
ADMIN KNOWLEDGE INGESTION SCRIPT
Run this to ingest PDFs into the RAG knowledge base.
Farmers NEVER see this. This is admin-only.

Usage:
  python scripts/admin_ingest.py --file path/to/file.pdf --crop wheat --lang en
  python scripts/admin_ingest.py --dir knowledge_docs/
"""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.pipeline import RAGPipeline

def ingest_file(path: str, crop: str = "general", language: str = "en"):
    rag = RAGPipeline()
    meta = {"filename": os.path.basename(path), "crop": crop, "language": language, "doc_type": "admin"}
    count = rag.ingest(path, meta)
    print(f"✅ Ingested: {path} → {count} chunks")

def ingest_dir(directory: str):
    for fname in os.listdir(directory):
        if fname.endswith((".pdf", ".txt")):
            ingest_file(os.path.join(directory, fname))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Single PDF file")
    parser.add_argument("--dir", help="Directory of PDFs")
    parser.add_argument("--crop", default="general")
    parser.add_argument("--lang", default="en")
    args = parser.parse_args()
    if args.file: ingest_file(args.file, args.crop, args.lang)
    elif args.dir: ingest_dir(args.dir)
    else: print("Usage: python scripts/admin_ingest.py --file x.pdf OR --dir ./docs")
