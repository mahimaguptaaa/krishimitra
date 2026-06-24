from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from models import Document
from middleware.auth_middleware import get_current_user
from rag.pipeline import RAGPipeline
from pydantic import BaseModel
from config import settings
from pathlib import Path
import uuid, shutil

router = APIRouter()
rag = RAGPipeline()

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    crop_tag: str = Form(default=""),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")

    upload_dir = Path(settings.UPLOAD_DIR) / "docs"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename  = f"{uuid.uuid4()}_{file.filename}"
    save_path = upload_dir / filename

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = Document(
        id=uuid.uuid4(), user_id=uuid.UUID(user_id),
        filename=file.filename, file_path=str(save_path),
        crop_tag=crop_tag, status="pending"
    )
    db.add(doc)
    await db.commit()

    # Index in background
    background_tasks.add_task(
        index_document, str(doc.id), str(save_path),
        {"filename": file.filename, "crop": crop_tag}, db
    )

    return {"doc_id": str(doc.id), "status": "processing",
            "message": "Document queued for indexing. Ready in ~30 seconds."}

async def index_document(doc_id: str, file_path: str, metadata: dict, db: AsyncSession):
    from database.connection import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            chunk_count = rag.ingest(file_path, metadata)
            result = await session.execute(select(Document).where(Document.id == uuid.UUID(doc_id)))
            doc = result.scalar_one_or_none()
            if doc:
                doc.status = "indexed"
                doc.chunk_count = chunk_count
                await session.commit()
        except Exception as e:
            result = await session.execute(select(Document).where(Document.id == uuid.UUID(doc_id)))
            doc = result.scalar_one_or_none()
            if doc:
                doc.status = "failed"
                await session.commit()

class SearchRequest(BaseModel):
    query: str

@router.post("/search")
async def search_knowledge(
    body: SearchRequest,
    user_id: str = Depends(get_current_user)
):
    result = await rag.answer(body.query)
    return result

@router.get("/documents")
async def list_documents(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document).where(Document.user_id == uuid.UUID(user_id))
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    return {"documents": [
        {"id": str(d.id), "filename": d.filename, "status": d.status,
         "chunk_count": d.chunk_count, "crop_tag": d.crop_tag, "created_at": str(d.created_at)}
        for d in docs
    ]}
