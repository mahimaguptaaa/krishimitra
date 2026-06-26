from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user
import shutil, tempfile, os, logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/stt")
async def stt(
    audio: UploadFile = File(...),
    language: str = Form(default="hi"),
    uid: str = Depends(get_current_user)
):
    # Lazy import - WhisperSTT loads faster-whisper model only when needed
    from voice.stt import WhisperSTT
    stt_ = WhisperSTT()
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as t:
        shutil.copyfileobj(audio.file, t)
        path = t.name
    try:
        result = stt_.transcribe(path, language=language or "hi")
        return result
    except Exception as e:
        logger.error(f"STT failed: lang={language} error={e}")
        raise HTTPException(status_code=502, detail=f"STT failed: {e}")
    finally:
        os.unlink(path)


class TTSReq(BaseModel):
    text: str
    language: str = "hi"


@router.post("/tts")
async def tts_route(b: TTSReq, uid: str = Depends(get_current_user)):
    # Lazy import - TTS loads gTTS only when needed
    from voice.tts import MultilingualTTS
    tts = MultilingualTTS()
    try:
        audio = tts.synthesize(b.text, b.language)
        return Response(content=audio, media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"TTS failed: lang={b.language} error={type(e).__name__}: {e}")
        raise HTTPException(status_code=502, detail=f"TTS failed: {e}")