from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from middleware.auth_middleware import get_current_user
from analytics.query_analytics import QueryAnalytics

router = APIRouter()
analytics = QueryAnalytics()

@router.get("/agents")
async def agent_usage(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await analytics.top_agents(db)

@router.get("/diseases")
async def disease_trends(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await analytics.top_diseases(db)

@router.get("/usage")
async def daily_usage(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await analytics.daily_usage(db)

@router.get("/summary")
async def summary(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return {
        "top_agents":   await analytics.top_agents(db),
        "top_diseases": await analytics.top_diseases(db),
        "daily_usage":  await analytics.daily_usage(db),
        "avg_latency_ms": await analytics.avg_response_time(db),
    }
