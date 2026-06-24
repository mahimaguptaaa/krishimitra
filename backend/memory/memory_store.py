"""
MEMORY STORE — single entry point to access all farmer memory
Injected into agent context before each query.
"""
from memory.farmer_profile import FarmerProfileManager
from memory.conversation_memory import ConversationMemory
from sqlalchemy.ext.asyncio import AsyncSession

class MemoryStore:
    def __init__(self):
        self.profile_mgr = FarmerProfileManager()
        self.conv_memory  = ConversationMemory(window=6)

    async def build_context(self, user_id: str, chat_id: str, db: AsyncSession) -> dict:
        """Build full context dict injected into every agent."""
        profile = await self.profile_mgr.get(user_id, db)
        conv    = await self.conv_memory.get_summary(chat_id, db) if chat_id else ""
        return {
            "state":              profile.get("location", "India"),
            "crops":              profile.get("crops", []),
            "soil_type":          profile.get("soil_type", ""),
            "irrigation_type":    profile.get("irrigation_type", ""),
            "land_area_acres":    profile.get("land_area_acres"),
            "farmer_language":    profile.get("language", "hi"),
            "conversation_history": conv,
        }
