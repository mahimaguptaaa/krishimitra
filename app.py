from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import faiss
import ollama
import sqlite3
from datetime import datetime
from sentence_transformers import SentenceTransformer

app = FastAPI()
# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("questions.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    question TEXT,
    timestamp TEXT
)
""")
conn.commit()
# ------------------------------------------------
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
    phone: str

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

        # Save question in DB
    cursor.execute(
        "INSERT INTO history (phone, question, timestamp) VALUES (?, ?, ?)",
        (q.phone, query, datetime.now().isoformat())
    )
    conn.commit()

    return {"answer": response["message"]["content"]}

@app.get("/history/{phone}")
def get_history(phone: str):
    cursor.execute(
        "SELECT question FROM history WHERE phone=? ORDER BY id DESC",
        (phone,)
    )
    rows = cursor.fetchall()
    return {"history": [r[0] for r in rows]}