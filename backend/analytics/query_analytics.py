"""
QUERY ANALYTICS — tracks what farmers ask, which agents are used, disease trends
Stored in PostgreSQL. Lightweight, no external service needed.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from models import AgentLog, DiseasePrediction, Message
import uuid

class QueryAnalytics:
    async def top_agents(self, db: AsyncSession, days: int = 30) -> list:
        """Which agents are used most?"""
        result = await db.execute(text(f"""
            SELECT agent_name, COUNT(*) as count
            FROM agent_logs
            WHERE created_at > NOW() - INTERVAL '{days} days'
            GROUP BY agent_name ORDER BY count DESC
        """))
        return [{"agent": r.agent_name, "count": r.count} for r in result]

    async def top_diseases(self, db: AsyncSession, days: int = 30) -> list:
        """Most detected diseases."""
        result = await db.execute(text(f"""
            SELECT disease_name, COUNT(*) as count, AVG(confidence) as avg_confidence
            FROM disease_predictions
            WHERE created_at > NOW() - INTERVAL '{days} days'
            AND disease_name IS NOT NULL
            GROUP BY disease_name ORDER BY count DESC LIMIT 10
        """))
        return [{"disease": r.disease_name, "count": r.count, "avg_confidence": round(r.avg_confidence or 0, 2)} for r in result]

    async def daily_usage(self, db: AsyncSession, days: int = 7) -> list:
        """Messages per day."""
        result = await db.execute(text(f"""
            SELECT DATE(created_at) as date, COUNT(*) as messages
            FROM messages
            WHERE created_at > NOW() - INTERVAL '{days} days'
            AND role = 'user'
            GROUP BY DATE(created_at) ORDER BY date
        """))
        return [{"date": str(r.date), "messages": r.messages} for r in result]

    async def avg_response_time(self, db: AsyncSession) -> float:
        result = await db.execute(text("SELECT AVG(latency_ms) FROM agent_logs WHERE latency_ms IS NOT NULL"))
        val = result.scalar()
        return round(val or 0, 1)
