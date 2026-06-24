"""
CONVERSATION MEMORY — stores last N messages per session
Used to give agents context of what was discussed earlier.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Message
import uuid

class ConversationMemory:
    def __init__(self, window: int = 6):
        self.window = window   # how many past messages to include

    async def get_context(self, chat_id: str, db: AsyncSession) -> str:
        """Return last N messages as a formatted string."""
        result = await db.execute(
            select(Message)
            .where(Message.chat_id == uuid.UUID(chat_id))
            .order_by(Message.created_at.desc())
            .limit(self.window)
        )
        messages = list(reversed(result.scalars().all()))
        if not messages:
            return ""
        lines = []
        for m in messages:
            role = "Farmer" if m.role == "user" else "KrishiMitra"
            lines.append(f"{role}: {m.content[:300]}")
        return "\n".join(lines)

    async def get_summary(self, chat_id: str, db: AsyncSession) -> str:
        """Summarize recent conversation for agent context injection."""
        context = await self.get_context(chat_id, db)
        if not context:
            return ""
        return f"Previous conversation:\n{context}\n"
