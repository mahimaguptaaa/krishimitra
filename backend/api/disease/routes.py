from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from models import DiseasePrediction
from middleware.auth_middleware import get_current_user
from agents.disease_agent import DiseaseAgent
from config import settings
from pathlib import Path
import uuid, shutil

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}

@router.post("/predict")
async def predict_disease(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG images allowed")

    # Save uploaded image
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    filename  = f"{uuid.uuid4()}{Path(file.filename).suffix}"
    save_path = upload_dir / filename

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Run disease agent
    from agents.disease_agent import DiseaseAgent
    agent  = DiseaseAgent()
    result = await agent.run("", {"image_path": str(save_path)})

    # Save prediction to DB
    meta = result.get("metadata", {})
    if meta.get("not_a_crop"):
        return {
            "prediction_id": None,
            "disease_name": None,
            "confidence": meta.get("confidence", 0),
            "top_k": [],
            "report": "यह छवि किसी फसल या पौधे की नहीं लगती। कृपया अपनी फसल की स्पष्ट फोटो अपलोड करें। 🌱",
            "not_a_crop": True,
        }
    pred = DiseasePrediction(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        image_path=str(save_path),
        disease_name=meta.get("disease_name"),
        confidence=meta.get("confidence"),
        top_k=meta.get("top_k"),
        llm_report=result["response"],
    )
    db.add(pred)
    await db.commit()

    return {
        "prediction_id": str(pred.id),
        "disease_name": meta.get("disease_name", "Unknown"),
        "confidence": meta.get("confidence", 0),
        "top_k": meta.get("top_k", []),
        "report": result["response"],
    }

@router.get("/history")
async def disease_history(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DiseasePrediction)
        .where(DiseasePrediction.user_id == uuid.UUID(user_id))
        .order_by(DiseasePrediction.created_at.desc())
        .limit(20)
    )
    preds = result.scalars().all()
    return {"predictions": [
        {"id": str(p.id), "disease_name": p.disease_name,
         "confidence": p.confidence, "created_at": str(p.created_at)}
        for p in preds
    ]}
