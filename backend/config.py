from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/krishimitra"
    SECRET_KEY: str = "change-this-secret"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OPENWEATHER_KEY: str = ""
    DATA_GOV_IN_KEY: str = "579b464db66ec23bdd000001cdd3946e44ce4aad38034a291041822"
    # "small" is fast but weak on Gujarati/Telugu/Punjabi voice recognition.
    # Use "medium" for noticeably better accuracy (slower, more RAM).
    WHISPER_MODEL_SIZE: str = "small"
    UPLOAD_DIR: str = "uploads"
    FAISS_DIR: str = "data"
    DEBUG: bool = True
    class Config: env_file = ".env"

settings = Settings()
