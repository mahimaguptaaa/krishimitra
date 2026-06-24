from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from database.connection import get_db
from models import User
from services.auth_service import create_token
import uuid, random, time

router = APIRouter()
_otp_store: dict = {}   # phone -> {otp, expires, name, attempts}
PHONE_NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")

def phone_to_uuid(phone: str) -> uuid.UUID:
    return uuid.uuid5(PHONE_NAMESPACE, phone)

class SendOTPReq(BaseModel):
    phone: str
    name: str = "Farmer"

class VerifyOTPReq(BaseModel):
    phone: str
    otp: str

@router.post("/send-otp")
async def send_otp(body: SendOTPReq):
    otp = str(random.randint(1000, 9999))
    _otp_store[body.phone] = {
        "otp": otp, "expires": time.time() + 300,
        "name": body.name or "Farmer", "attempts": 0,
    }
    print(f"[OTP] Phone: {body.phone} Name: {body.name} OTP: {otp}")
    return {"success": True, "message": "OTP sent", "debug_otp": otp}

@router.post("/verify-otp")
async def verify_otp(body: VerifyOTPReq, db: AsyncSession = Depends(get_db)):
    # FIX #2: actually validate the OTP -- previously ANY 4-digit code
    # was silently accepted (a leftover demo fallback on the frontend),
    # which let users in with wrong codes.
    record = _otp_store.get(body.phone)

    if not record:
        raise HTTPException(status_code=400, detail="OTP expired or not requested. Please request a new OTP.")

    if time.time() > record["expires"]:
        del _otp_store[body.phone]
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    record["attempts"] += 1
    if record["attempts"] > 5:
        del _otp_store[body.phone]
        raise HTTPException(status_code=429, detail="Too many wrong attempts. Please request a new OTP.")

    if body.otp != record["otp"]:
        raise HTTPException(status_code=400, detail="Incorrect OTP. Please check and try again.")

    # OTP correct -- consume it so it can't be reused
    name = record["name"]
    del _otp_store[body.phone]

    user_id = phone_to_uuid(body.phone)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=user_id, name=name,
            email=f"{body.phone}@krishimitra.local",
            password_hash="otp-login-no-password",
            language="hi", state="", crops=[],
        )
        db.add(user)
        await db.commit()
    elif name and name != "Farmer" and user.name != name:
        user.name = name
        await db.commit()

    token = create_token(str(user.id))
    return {"access_token": token, "user": {"id": str(user.id), "name": user.name, "phone": body.phone, "language": user.language}}
