from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user
from voice.tts import MultilingualTTS
from voice.stt import WhisperSTT
import shutil, tempfile, os

router = APIRouter()
tts = MultilingualTTS()

@router.post("/stt")
async def stt(
    audio: UploadFile = File(...),
    language: str = Form(default="hi"),
    uid: str = Depends(get_current_user)
):
    stt_ = WhisperSTT()
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as t:
        shutil.copyfileobj(audio.file, t)
        path = t.name
    try:
        return stt_.transcribe(path, language=language or "hi")
    finally:
        os.unlink(path)

class TTSReq(BaseModel):
    text: str
    language: str = "hi"

@router.post("/tts")
async def tts_route(b: TTSReq, uid: str = Depends(get_current_user)):
    try:
        audio = tts.synthesize(b.text, b.language)
        return Response(content=audio, media_type="audio/mpeg")
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            f"TTS failed: lang={b.language} error={type(e).__name__}: {e}"
        )
        raise HTTPException(
            status_code=502,
            detail=f"TTS failed: {e}"
        )
