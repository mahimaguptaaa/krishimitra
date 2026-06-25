from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database only at startup
    await init_db()
    yield

app = FastAPI(
    title="KrishiMitra",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://krishii-mitra.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Import routers lazily inside functions to reduce startup memory
from api.auth.otp_routes import router as auth_router
from api.chat.routes import router as chat_router
from api.disease.routes import router as disease_router
from api.disease.chat_route import router as disease_chat_router
from api.weather.routes import router as weather_router
from api.knowledge.routes import router as knowledge_router
from api.voice.routes import router as voice_router
from api.market.routes import router as market_router
from api.analytics.routes import router as analytics_router

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(disease_router, prefix="/api/disease", tags=["Disease"])
app.include_router(disease_chat_router, prefix="/api/disease", tags=["Disease Chat"])
app.include_router(weather_router, prefix="/api/weather", tags=["Weather"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["Knowledge"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])
app.include_router(market_router, prefix="/api/market", tags=["Market"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
def health():
    return {"status": "ok", "project": "KrishiMitra"}