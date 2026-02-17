import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# 🔹 Load embedding model (same one used earlier)
print("Loading embedding model...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# 🔹 Load FAISS index
index = faiss.read_index("krishi_index.faiss")

# 🔹 Load original dataset
with open("krishimitra_full_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [item["text"] for item in data]

print("System ready!")

# 🔹 Ask farmer question
query = input("\n👨‍🌾 Enter farmer question: ")

# 🔹 Convert question into embedding
query_vector = model.encode([query])
query_vector = np.array(query_vector).astype("float32")

# 🔹 Search FAISS (top 3 results)
k = 3
distances, indices = index.search(query_vector, k)

print("\n🔎 Most relevant answers:\n")

for i, idx in enumerate(indices[0]):
    print(f"Result {i+1}:")
    print(texts[idx])
    print("-" * 50)