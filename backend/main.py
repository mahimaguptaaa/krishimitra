from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import init_db

from api.auth.otp_routes import router as auth_router
from api.chat.routes import router as chat_router

from api.disease.routes import router as disease_router
from api.disease.chat_route import router as disease_chat_router

from api.weather.routes import router as weather_router
from api.knowledge.routes import router as knowledge_router
from api.voice.routes import router as voice_router
from api.market.routes import router as market_router
from api.analytics.routes import router as analytics_router

app = FastAPI(
    title="KrishiMitra",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await init_db()

# Auth
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Auth"]
)

# Chat
app.include_router(
    chat_router,
    prefix="/api/chat",
    tags=["Chat"]
)

# Disease Detection
app.include_router(
    disease_router,
    prefix="/api/disease",
    tags=["Disease"]
)

# Disease Detection (Chat Upload Endpoint)
app.include_router(
    disease_chat_router,
    prefix="/api/disease",
    tags=["Disease Chat"]
)

# Weather
app.include_router(
    weather_router,
    prefix="/api/weather",
    tags=["Weather"]
)

# Knowledge
app.include_router(
    knowledge_router,
    prefix="/api/knowledge",
    tags=["Knowledge"]
)

# Voice
app.include_router(
    voice_router,
    prefix="/api/voice",
    tags=["Voice"]
)

# Market
app.include_router(
    market_router,
    prefix="/api/market",
    tags=["Market"]
)

# Analytics
app.include_router(
    analytics_router,
    prefix="/api/analytics",
    tags=["Analytics"]
)

@app.get("/")
def health():
    return {
        "status": "ok",
        "project": "KrishiMitra 2.0 Final"
    }