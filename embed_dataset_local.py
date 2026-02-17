import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# 🔹 Load local embedding model
print("Loading embedding model...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# 🔹 Load dataset
with open("krishimitra_full_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [item["text"] for item in data]

print(f"Total entries: {len(texts)}")

# 🔹 Generate embeddings locally
print("Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True)

# 🔹 Convert to numpy array
embeddings = np.array(embeddings).astype("float32")

# 🔹 Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# 🔹 Add embeddings to index
index.add(embeddings)

# 🔹 Save index
faiss.write_index(index, "krishi_index.faiss")

print("\n✅ Embeddings created successfully!")
print("FAISS index saved as krishi_index.faiss")
