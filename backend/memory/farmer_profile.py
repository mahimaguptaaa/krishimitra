"""
FARMER PROFILE — stores persistent facts about each farmer
Extracted from conversations automatically.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import FarmerProfile as FarmerProfileModel
from services.llm_service import LLMService
import uuid, json

EXTRACT_PROMPT = """
Extract structured farmer profile information from this message if present.
Return ONLY a JSON object with these keys (omit keys not mentioned):
{{
  "crops": ["wheat"],
  "location": "Kanpur",
  "land_area_acres": 5,
  "soil_type": "loamy",
  "irrigation_type": "drip",
  "language": "hi"
}}

Message: {message}

Return {{}} if no profile info found.
"""

class FarmerProfileManager:
    def __init__(self):
        self.llm = LLMService()

    async def extract_and_update(self, user_id: str, message: str, db: AsyncSession):
        """Auto-extract profile facts from farmer message and save."""
        try:
            raw = self.llm.complete(EXTRACT_PROMPT.format(message=message))
            import re
            match = re.search(r"\{.*?\}", raw, re.DOTALL)
            if not match:
                return
            updates = json.loads(match.group())
            if not updates:
                return
            await self._save(user_id, updates, db)
        except Exception:
            pass

    async def _save(self, user_id: str, updates: dict, db: AsyncSession):
        result = await db.execute(
            select(FarmerProfileModel).where(FarmerProfileModel.user_id == uuid.UUID(user_id))
        )
        profile = result.scalar_one_or_none()
        if profile:
            for k, v in updates.items():
                if hasattr(profile, k) and v:
                    setattr(profile, k, v)
        else:
            profile = FarmerProfileModel(
                id=uuid.uuid4(), user_id=uuid.UUID(user_id), **updates
            )
            db.add(profile)
        await db.commit()

    async def get(self, user_id: str, db: AsyncSession) -> dict:
        print("\n========== DEBUG ==========")
        print("USER_ID =", user_id)
        print("TYPE =", type(user_id))
        print("===========================\n")
        result = await db.execute(
            select(FarmerProfileModel).where(FarmerProfileModel.user_id == uuid.UUID(user_id))
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return {}
        return {
            "crops":          profile.crops or [],
            "location":       profile.location or "",
            "land_area_acres":profile.land_area_acres,
            "soil_type":      profile.soil_type or "",
            "irrigation_type":profile.irrigation_type or "",
            "language":       profile.language or "hi",
        }
