from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import faiss
import ollama
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models at startup
embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
index = faiss.read_index("krishi_index.faiss")

with open("krishimitra_full_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [item["text"] for item in data]

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_ai(q: Question):
    query = q.question

    query_vector = embed_model.encode([query])
    query_vector = np.array(query_vector).astype("float32")

    distances, indices = index.search(query_vector, 3)
    context = "\n\n".join([texts[i] for i in indices[0]])

    prompt = f"""
You are an agriculture expert helping Indian farmers.

Answer ONLY using the provided context.
If answer is not found, say you don't know.

CONTEXT:
{context}

QUESTION:
{query}

Answer in simple Hindi.
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"answer": response["message"]["content"]}