from fastapi import APIRouter, Depends, Query
from middleware.auth_middleware import get_current_user
from agents.market_agent import MarketAgent
from pydantic import BaseModel

router = APIRouter()

class MarketQuery(BaseModel):
    question: str
    crop: str = ""
    location: str = "India"

@router.post("/query")
async def market_query(body: MarketQuery, user_id: str = Depends(get_current_user)):
    agent = MarketAgent()
    result = await agent.run(body.question, {"crops": [body.crop] if body.crop else [], "state": body.location})
    return result

@router.get("/prices")
async def get_prices(crop: str = Query(...), state: str = Query(default="India"), user_id: str = Depends(get_current_user)):
    agent = MarketAgent()
    prices = await agent._fetch_prices([crop], state)
    return {"crop": crop, "state": state, "data": prices}
