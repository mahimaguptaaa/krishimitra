import json
import numpy as np
import faiss
import ollama
from sentence_transformers import SentenceTransformer

# Load embedding model
embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Load FAISS index
index = faiss.read_index("krishi_index.faiss")

# Load dataset
with open("krishimitra_full_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [item["text"] for item in data]

print("✅ Local AI system ready!")

while True:
    query = input("\n👨‍🌾 Ask farmer question (type exit to quit): ")

    if query.lower() == "exit":
        break

    # Convert query into embedding
    query_vector = embed_model.encode([query])
    query_vector = np.array(query_vector).astype("float32")

    # Retrieve top matches
    k = 3
    distances, indices = index.search(query_vector, k)

    context = "\n\n".join([texts[i] for i in indices[0]])

    # Build RAG prompt
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

    # Call local LLM
    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    print("\n🤖 AI Answer:\n")
    print(response["message"]["content"])