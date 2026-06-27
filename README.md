# 🌾 KrishiMitra — AI Agricultural Advisory System

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-krishii--mitra.netlify.app-green?style=for-the-badge)](https://krishii-mitra.netlify.app)
[![Backend](https://img.shields.io/badge/_Backend-HuggingFace_Spaces-yellow?style=for-the-badge)](https://mahimaguptaa-krishimitra.hf.space)
[![GitHub](https://img.shields.io/badge/GitHub-mahimaguptaaa%2Fkrishimitra-black?style=for-the-badge&logo=github)](https://github.com/mahimaguptaaa/krishimitra)

---

## 📖 About

**KrishiMitra** (कृषि-मित्र) is a voice-first, multilingual AI chatbot that provides agricultural advisory services to Indian farmers in their native language.

India has 700+ million farmers, most of whom speak regional languages and have no easy access to expert farming advice. KrishiMitra bridges this gap by allowing farmers to ask questions about crops, diseases, weather, government schemes, and market prices — by voice or text — in 10 Indian languages.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎤 **Voice Input (STT)** | Speak questions in your language using faster-whisper with explicit language hints |
| 🔊 **Voice Output (TTS)** | Listen to answers via gTTS in 10 Indian languages |
| 🌐 **9 Languages** | Hindi, English, Punjabi, Gujarati, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam |
| 🌿 **Crop Disease Detection** | Upload plant photo → EfficientNet-B0 detects disease from 38 PlantVillage classes |
| 🛡️ **Smart Image Validation** | Groq Vision pre-checks if image is an actual crop before disease detection |
| 🧠 **RAG Knowledge Base** | FAISS vector search over ICAR agricultural PDFs with cross-encoder re-ranking |
| 🌦️ **Weather Advisory** | Location-based weather info for farming decisions via OpenWeatherMap |
| 📈 **Market Prices** | Real-time mandi prices via Data.gov.in API |
| 📞 **Farmer Helplines** | Direct access to PM-KISAN, Fasal Bima, and Kisan Call Centre numbers |
| 🌙 **Dark Mode** | User-specific theme persistence per account |
| 📱 **Mobile Responsive** | Farmer-friendly UI optimized for low-end Android devices |

---

## 🖥️ Application Screenshots

### Language Selection
<img width="948" height="438" alt="Screenshot 2026-06-26 185435" src="https://github.com/user-attachments/assets/ea004a47-d008-4534-a2a6-e44429d3089d" />

*Farmers can choose from multiple Indian languages including Hindi, English, Punjabi, Marathi, Bengali, Tamil, Telugu, Gujarati, Kannada, and Malayalam. Voice guidance is available for every language option to improve accessibility.*

### OTP Login
<img width="955" height="438" alt="Screenshot 2026-06-26 185502" src="https://github.com/user-attachments/assets/09850b58-f223-432b-9cce-b2652dcc4668" />


<img width="952" height="438" alt="Screenshot 2026-06-26 185535" src="https://github.com/user-attachments/assets/e402d795-fc76-44e6-b88a-ca84d11bb569" />


*Simple phone number + OTP authentication — no password needed.*

### Location Setup
<img width="952" height="440" alt="Screenshot 2026-06-26 185653" src="https://github.com/user-attachments/assets/b7adaa29-77fd-4a69-82f9-04e2ab0b0f94" />

*During onboarding, users can provide their village or district. This information helps KrishiMitra provide location-specific recommendations, weather updates, and agricultural guidance.*

### Crop Selection
<img width="950" height="431" alt="Screenshot 2026-06-26 185717" src="https://github.com/user-attachments/assets/a13670cb-4af7-4b16-a783-0dca268e4e7d" />

*Farmers can specify the crops they cultivate, such as wheat, rice, vegetables, or fruits. The AI uses this information to personalize recommendations and provide crop-specific assistance.*

### Interactive Tutorial
<img width="956" height="437" alt="Screenshot 2026-06-26 185756" src="https://github.com/user-attachments/assets/6c1f3637-57f8-41d4-a647-63178f5229be" />

A built-in guided tutorial explains how to use the platform, this makes the platform easy to use even for first-time users.

### Chat Interface
<img width="955" height="436" alt="Screenshot 2026-06-26 185820" src="https://github.com/user-attachments/assets/1e276e5c-9526-477c-b873-0694a5e8d8f6" />

*KrishiMitra's intelligent dashboard for asking questions, diagnosing crops, and receiving expert farming recommendations with voice input/output.*

### Crop Disease Detection
<img width="956" height="421" alt="Screenshot 2026-06-26 192448" src="https://github.com/user-attachments/assets/6b24a1f9-b403-4f68-b1da-e9f61e3cb10e" />


<img width="953" height="436" alt="Screenshot 2026-06-26 192624" src="https://github.com/user-attachments/assets/7a7bdcd9-d0d3-47f2-bc99-10b7084c4f60" />


<img width="958" height="438" alt="Screenshot 2026-06-26 192641" src="https://github.com/user-attachments/assets/2c6685fd-dffd-44c7-861f-a967b9a831cc" />



*Upload a crop photo → AI identifies disease and gives treatment advice.*

### Chat History
<img width="957" height="436" alt="Screenshot 2026-06-26 190315" src="https://github.com/user-attachments/assets/9157af42-eec4-4164-a8e1-3f00c539ff21" />

*All previous conversations saved and accessible.*

### Settings
<img width="949" height="436" alt="Screenshot 2026-06-26 185903" src="https://github.com/user-attachments/assets/e5158ad2-bb3c-466d-aff4-80475ec5af97" />


<img width="955" height="434" alt="Screenshot 2026-06-26 185925" src="https://github.com/user-attachments/assets/2d642d0f-763f-414f-835a-5643f2b446ca" />


*Language switcher, dark mode toggle, voice speed control, font size.*

### Farmer Helplines
<img width="948" height="434" alt="Screenshot 2026-06-26 185847" src="https://github.com/user-attachments/assets/969e97a3-7c5e-4469-b355-2197c34a5073" />

*Direct access to government agricultural helpline numbers.*

---

## 🧠 How It Works

```
Farmer speaks/types question
         ↓
  STT (faster-whisper)
         ↓
   Orchestrator Agent
         ↓
  ┌──────────────────────────────────────┐
  │  CropAdvisorAgent                    │
  │  DiseaseAgent (+ Vision pre-check)   │
  │  WeatherAgent                        │
  │  MarketPriceAgent                    │
  │  RAG Pipeline (FAISS + ICAR PDFs)    │
  └──────────────────────────────────────┘
         ↓
  LLM Service (Gemini → Groq → Ollama)
         ↓
  Translation Service (LLM-based, Unicode script validated)
         ↓
  TTS (gTTS) → Audio response
         ↓
  Farmer hears answer in their language
```

---

## 🏗️ Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **Tailwind CSS**
- **Zustand** (state management)
- **react-i18next** (UI localization)

### Backend
- **FastAPI** (async Python API)
- **SQLAlchemy + asyncpg** (async ORM)
- **PostgreSQL** on Neon.tech

### AI / ML
- **Google Gemini 2.5 Flash** — Primary LLM
- **Groq llama-3.1-8b** — Fallback LLM
- **Groq llama-3.2-11b-vision** — Crop image pre-validation
- **Ollama (qwen2.5)** — Local fallback
- **faster-whisper** — Speech-to-Text
- **gTTS** — Text-to-Speech (10 languages)
- **EfficientNet-B0** — Disease detection (38 classes, PlantVillage)
- **FAISS** — Vector search for RAG
- **Sentence-transformers** — Document embeddings

### Infrastructure
- **Hugging Face Spaces** (Docker backend)
- **Netlify** (Next.js frontend)
- **Neon.tech** (PostgreSQL)
- **Docker** (containerization)

---

## 🔑 Key Engineering Decisions

| Challenge | Solution |
|---|---|
| Indic TTS gibberish | Script validation before gTTS + correct IETF lang codes |
| LLM producing romanized Indic text | Explicit Unicode script name in translation prompt + retry |
| Crop hallucinations | Dynamic prompt from farmer profile; "None registered" fallback |
| Non-crop image false detections | Used Groq Vision as primary image validator with Gemini vision as fallback, pre-checks → blocks scenery/flowers before EfficientNet |
| STT wrong language output | Explicit language hint to faster-whisper, never auto-detect |
| 3-tier LLM fallback | Gemini → Groq → Ollama ensures 99%+ uptime |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 
- Gemini API key 
- Groq API key 

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your API keys

# Run migrations
python -c "from database.connection import init_db; import asyncio; asyncio.run(init_db())"

# Ingest knowledge base PDFs
python scripts/admin_ingest.py --dir knowledge_docs/

# Start server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

### Docker (Full Stack)

```bash
docker-compose up
```

---

## 🌾 Example Questions

| Language | Question |
|---|---|
| Hindi | गेहूं में पहली खाद कब डालें? |
| Punjabi | ਕਣਕ ਵਿੱਚ ਖਾਦ ਕਦੋਂ ਪਾਉਣੀ ਚਾਹੀਦੀ ਹੈ? |
| Gujarati | ટામેટામાં ફૂલ કેમ ખરી જાય છે? |
| Telugu | వరి పంటలో తెగులు ఎలా నివారించాలి? |
| English | What fertilizer should I use for rice? |

---

## 📊 Project Numbers

- **10** supported Indian languages
- **38** disease classes (PlantVillage dataset)
- **3** LLM fallback tiers
- **2** image validation layers
- **4** ICAR agricultural PDFs ingested
- **5** specialized AI agents

---

## 🗂️ Project Structure

```
krishimitra/
├── backend/
│   ├── agents/          # CropAdvisor, Disease, Weather, Market agents
│   ├── api/             # FastAPI routes (auth, chat, disease, voice, etc.)
│   ├── ml/              # EfficientNet-B0 disease model
│   ├── rag/             # FAISS pipeline, embedder, splitter
│   ├── services/        # LLM, translation, auth services
│   ├── voice/           # STT (Whisper) and TTS (gTTS)
│   └── main.py
├── frontend/
│   ├── app/             # Next.js App Router pages
│   ├── components/      # UI components
│   ├── store/           # Zustand stores
│   └── i18n/locales/    # Translation files (10 languages)
└── docker/
    ├── Dockerfile.backend
    └── Dockerfile.frontend
```

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 👩‍💻 Author

**Mahima Gupta**

[GitHub](https://github.com/mahimaguptaaa) | [Live Demo](https://krishii-mitra.netlify.app)
