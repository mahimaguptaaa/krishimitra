"""
Extra route: /api/disease/predict-chat
Same as predict but returns chat-friendly response format.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from models import DiseasePrediction
from middleware.auth_middleware import get_current_user
from config import settings
from pathlib import Path
import uuid, shutil

router = APIRouter()

@router.post("/predict-chat")
async def predict_chat(
    file: UploadFile = File(...),
    message: str = Form(default=""),
    language: str = Form(default="en"),
    uid: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
    fname = f"{uuid.uuid4()}{Path(file.filename).suffix}"
    path = str(Path(settings.UPLOAD_DIR) / fname)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Lazy imports to prevent memory crash at startup
    from agents.disease_agent import DiseaseAgent
    from services.translation_service import TranslationService

    res = await DiseaseAgent().run(
        message or "What disease is this?",
        {"image_path": path}
    )
    meta = res.get("metadata", {})

    tr = TranslationService()
    translated_response = tr.from_english(res["response"], language)

    db.add(DiseasePrediction(
        id=uuid.uuid4(), user_id=uuid.UUID(uid), image_path=path,
        disease_name=meta.get("disease"), confidence=meta.get("confidence"),
        top_k=meta.get("top_k"), llm_report=translated_response
    ))
    await db.commit()

    return {
        "response": translated_response,
        "agent_used": "DISEASE",
        "sources": res.get("sources", []),
        "language": language,
    }