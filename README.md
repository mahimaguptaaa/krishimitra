# 🌾 KrishiMitra AI – Intelligent Farming Assistant
<img width="1536" height="1024" alt="banner" src="https://github.com/user-attachments/assets/0daaa6c0-8136-4c08-a3d5-bccc566f218b" />

---

## 🚀 Overview

**KrishiMitra AI** is an intelligent agriculture assistant built to support farmers by providing **quick, reliable, and easy-to-understand answers** to farming-related queries in **simple Hindi**.

The system leverages a **Retrieval-Augmented Generation (RAG)** pipeline combined with a **local Large Language Model (Mistral via Ollama)** to ensure responses are **context-aware and grounded in real agricultural data**, rather than generic AI outputs.

To enhance accessibility, KrishiMitra also includes **voice-based interaction**, enabling farmers to both ask questions and receive answers through speech.

---

## 🎯 Key Highlights

* 📌 AI responses grounded in agriculture-specific dataset
* 🧠 RAG-based architecture for accurate information retrieval
* 🎤 Voice-enabled interaction for better accessibility
* ⚡ Fast and lightweight system using local LLM
* 🌐 Designed with a **farmer-first, simple UI approach**

---

## 🚜 Features

* 🌱 Ask agriculture-related questions in Hindi(or local languages)
* 🎤 Voice input using speech recognition
* 🔊 Text-to-Speech output for audio responses
* 🤖 AI-powered answers using Mistral (via Ollama)
* 🔎 Semantic search with FAISS vector database
* 📚 Custom agriculture knowledge dataset
* 💾 Chat history storage using SQLite
* 🌗 Light and Dark mode interface
* ⚙️ Language and UI customization
* 🌐 Clean and user-friendly interface

---

## 🧠 System Architecture

KrishiMitra AI follows a **Retrieval-Augmented Generation (RAG)** pipeline:

```id="rag-flow-pro"
Farmer Question (Text / Voice)
        ↓
Speech-to-Text Conversion
        ↓
Sentence Transformer Embedding
        ↓
FAISS Vector Search
        ↓
Relevant Context Retrieval
        ↓
Mistral LLM (via Ollama)
        ↓
Answer Generation (Hindi)
        ↓
Text-to-Speech Output
```

✔ Ensures **high relevance**
✔ Reduces hallucination
✔ Improves trust in AI responses

---

## 🖥️ Demo & Screenshots

### 🔐 Login Page

<img width="1916" height="975" alt="login-page" src="https://github.com/user-attachments/assets/c5915b58-54c4-4a06-88cd-10bcb8d2fd02" />


### 🏠 Main Interface

<img width="1919" height="912" alt="main-page" src="https://github.com/user-attachments/assets/08392305-74d3-45a8-a1d0-f8960dc686a2" />

---

### 🤖 AI Answer Generation

<img width="1913" height="981" alt="search-ans" src="https://github.com/user-attachments/assets/f279c672-dc37-490b-9d0d-5944ab13075a" />

---

### 🕘 Chat History

<img width="1892" height="908" alt="history-stored" src="https://github.com/user-attachments/assets/d5bec278-5ac8-48bf-99bd-488c3a5a9d07" />


---

### ⚙️ Settings Panel

<img width="1909" height="899" alt="settings-lang" src="https://github.com/user-attachments/assets/c3cbae24-cd74-4d2c-a369-ddf756f40450" />


---

### 🌙 Dark Mode

<img width="1907" height="915" alt="dark-mode" src="https://github.com/user-attachments/assets/3cd73266-f761-4c72-85e2-c46d12b5e1b9" />


---

## 🏗️ Tech Stack

### Backend

* Python
* FastAPI

### AI / ML

* Sentence Transformers
* FAISS Vector Database
* Ollama
* Mistral LLM

### Database

* SQLite

### Frontend

* HTML, CSS, JavaScript

### Voice Integration

* Browser Speech Recognition API
* Browser Text-to-Speech API

---

## 📂 Project Structure

```id="structure-pro"
krishimitra-ai/
│
├── app.py
├── database.py
├── rag_local_llm.py
├── embed_dataset_local.py
├── retrieve.py
│
├── krishimitra_full_dataset.json
├── krishi_index.faiss
│
├── index.html
├── main.html
│
├── images/
│   ├── login-page.png
│   ├── main-page.png
│   ├── search-ans.png
│   ├── history-stored.png
│   ├── dark-mode.png
│   └── settings-lang.png
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites

* Python 3.9+
* Ollama installed

### Installation

```id="setup-pro"
git clone https://github.com/yourusername/krishimitra-ai.git
cd krishimitra-ai
pip install -r requirements.txt
```

### Run the Model

```id="model-pro"
ollama pull mistral
```

### Generate Embeddings

```id="embed-pro"
python embed_dataset_local.py
```

### Start Server

```id="run-pro"
uvicorn app:app --reload
```

📍 Access the app at:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🌾 Sample Queries

* गेहूं में पहली खाद कब डालें?
* धान की रोपाई कब करें?
* फसल में कीट लग जाए तो क्या करें?
* टमाटर में फूल झड़ना कैसे रोकें?

---

## 🚀 Future Scope

* 📷 Crop disease detection using image input
* 🌦 Integration with real-time weather APIs
* 📱 Dedicated mobile application
* 🌍 Multi-language support

---

## 🤝 Contribution

Contributions are welcome!
Feel free to fork this repository and submit pull requests.

---
