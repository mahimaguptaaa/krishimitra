from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from database.connection import get_db
from models import User
from services.auth_service import hash_password, verify_password, create_token
import uuid

router = APIRouter()

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    state: str = ""
    language: str = "hi"
    crops: list = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=uuid.uuid4(),
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        state=body.state,
        language=body.language,
        crops=body.crops,
    )
    db.add(user)
    await db.commit()
    token = create_token(str(user.id))
    return {"access_token": token, "user": {"id": str(user.id), "name": user.name, "language": user.language}}

@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(str(user.id))
    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "name": user.name,
            "language": user.language,
            "state": user.state,
            "crops": user.crops,
        }
    }
