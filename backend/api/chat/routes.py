import re
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from database.connection import get_db
from models import Chat, Message, User, AgentLog
from middleware.auth_middleware import get_current_user
from middleware.rate_limiter import check_rate_limit
from agents.orchestrator import OrchestratorAgent
from services.translation_service import TranslationService
from services.llm_service import LLMService
from memory.memory_store import MemoryStore
from memory.farmer_profile import FarmerProfileManager
import uuid, time

router = APIRouter()
tr = TranslationService()
llm = LLMService()
orc = OrchestratorAgent()
mem = MemoryStore()
profiler = FarmerProfileManager()

# Language name + the ACTUAL SCRIPT it must be written in. This is the
# missing piece that caused "Hinglish" (Romanized Hindi) output -- the
# old prompt said "translate into Hindi" without specifying script, and
# Gemini sometimes defaults to Roman transliteration.
LANG_INFO = {
    "hi": ("Hindi",     "Devanagari", "जैसे: नमस्ते, आपकी फसल"),
    "en": ("English",   "Latin",      "e.g. Hello, your crop"),
    "pa": ("Punjabi",   "Gurmukhi",   "ਜਿਵੇਂ: ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਤੁਹਾਡੀ ਫ਼ਸਲ"),
    "mr": ("Marathi",   "Devanagari", "जसे: नमस्कार, तुमचे पीक"),
    "bn": ("Bengali",   "Bengali",    "যেমন: নমস্কার, আপনার ফসল"),
    "ta": ("Tamil",     "Tamil",      "எ.கா: வணக்கம், உங்கள் பயிர்"),
    "te": ("Telugu",    "Telugu",     "ఉదా: నమస్కారం, మీ పంట"),
    "gu": ("Gujarati",  "Gujarati",   "દા.ત: નમસ્તે, તમારો પાક"),
    "kn": ("Kannada",   "Kannada",    "ಉದಾ: ನಮಸ್ಕಾರ, ನಿಮ್ಮ ಬೆಳೆ"),
    "ml": ("Malayalam", "Malayalam",  "ഉദാ: നമസ്കാരം, നിങ്ങളുടെ വിള"),
}

TRANSLATE_PROMPT = """Translate the following agricultural advice into {lang_name}.

CRITICAL RULE: You MUST write the output using actual {script_name} Unicode
script characters ({sample}) -- NOT English/Roman letters. Do NOT write
Hinglish or any romanized/transliterated version. A farmer who only reads
{script_name} script must be able to read this directly.

Keep all numbers, dates, temperatures, percentages and units (mm, deg C,
kg, Rs, etc.) exactly as they are. Translate naturally, the way a native
{lang_name} speaker would say it -- not word for word.

Output ONLY the translated text in {script_name} script. No commentary,
no English explanation, no Roman letters except for numbers/units.

Text to translate:
{text}
"""

RETRY_PROMPT = """Your previous output was NOT in {script_name} script -- it used Roman/English
letters (Hinglish) instead. This is WRONG.

Rewrite the following text using ONLY {script_name} Unicode characters
({sample}). Every word must be in {script_name} script, not Roman letters.

Text to rewrite:
{text}
"""


class ChatReq(BaseModel):
    message: str
    chat_id: Optional[str] = None
    language: str = "hi"
    city: Optional[str] = "Delhi"
    image_path: Optional[str] = None


def _is_mostly_latin(text: str) -> bool:
    """Detect Hinglish/Romanized output -- if most letters are plain
    Latin a-z when they shouldn't be, the translation failed silently."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    latin = sum(1 for c in letters if c.isascii())
    return (latin / len(letters)) > 0.55


def translate_response(text: str, lang_code: str) -> str:
    if lang_code == "en" or not text.strip():
        return text

    lang_name, script_name, sample = LANG_INFO.get(lang_code, LANG_INFO["hi"])

    try:
        result = llm.complete(TRANSLATE_PROMPT.format(
            lang_name=lang_name, script_name=script_name, sample=sample, text=text
        )).strip()

        # FIX: safety net -- if the model still answered in Hinglish
        # (Roman letters) instead of the native script, retry once with
        # a more forceful correction prompt.
        if _is_mostly_latin(result):
            result = llm.complete(RETRY_PROMPT.format(
                script_name=script_name, sample=sample, text=result
            )).strip()

        # If it's STILL mostly Latin after retry, fall back to the
        # library translator rather than showing Hinglish.
        if _is_mostly_latin(result):
            return tr.from_english(text, lang_code)

        return result
    except Exception:
        return tr.from_english(text, lang_code)


@router.post("")
async def chat(b: ChatReq, uid: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    check_rate_limit(uid)
    await profiler.extract_and_update(uid, b.message, db)

    lang = b.language if b.language in LANG_INFO else tr.detect_language(b.message)
    msg_en = tr.to_english(b.message, lang)

    ctx = await mem.build_context(uid, b.chat_id, db)
    ctx["city"] = b.city or ctx.get("state", "Delhi")
    ctx["image_path"] = b.image_path

    cid = uuid.UUID(b.chat_id) if b.chat_id else uuid.uuid4()
    existing = await db.execute(select(Chat).where(Chat.id == cid))
    chat_obj = existing.scalar_one_or_none()
    if not chat_obj:
        chat_obj = Chat(id=cid, user_id=uuid.UUID(uid), title=b.message[:80])
        db.add(chat_obj)
        await db.flush()

    db.add(Message(id=uuid.uuid4(), chat_id=cid, role="user", content=b.message))

    t0 = time.time()
    res = await orc.route(msg_en, ctx)
    ms = int((time.time() - t0) * 1000)

    resp = translate_response(res["response"], lang)

    db.add(Message(id=uuid.uuid4(), chat_id=cid, role="assistant",
                    content=resp, agent_used=res.get("agent_used"), sources=res.get("sources", [])))
    db.add(AgentLog(id=uuid.uuid4(), user_id=uuid.UUID(uid),
                     agent_name=res.get("agent_used"), input_text=msg_en[:500],
                     output_text=res["response"][:500], latency_ms=ms))
    await db.commit()

    return {
        "chat_id": str(cid),
        "response": resp,
        "agent_used": res.get("agent_used"),
        "agents_consulted": res.get("agents_consulted", []),
        "sources": res.get("sources", []),
    }


@router.get("/history")
async def history(uid: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Chat).where(Chat.user_id == uuid.UUID(uid)).order_by(Chat.created_at.desc()))
    return {"chats": [{"id": str(c.id), "title": c.title, "created_at": str(c.created_at)} for c in r.scalars()]}


@router.get("/{chat_id}/messages")
async def msgs(chat_id: str, uid: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Message).where(Message.chat_id == uuid.UUID(chat_id)).order_by(Message.created_at))
    return {"messages": [{"role": m.role, "content": m.content, "agent_used": m.agent_used, "sources": m.sources} for m in r.scalars()]}
