"""
MARKET INTELLIGENCE AGENT
Uses Agmarknet (India Gov free API) for live mandi prices.
"""
import httpx
from agents.base_agent import BaseAgent
from services.llm_service import LLMService
from config import settings

MARKET_PROMPT = """
You are KrishiMitra's Market Intelligence Expert for Indian farmers.

Live Mandi Price Data:
{price_data}

Farmer Location: {location}
Farmer Crops: {crops}
Farmer Question: {query}

Give specific recommendations:
1. Best market to sell (with distance context if possible)
2. Current price comparison
3. Whether to sell now or wait (based on price trend if available)
4. Any quality tips that affect price

Be practical. Give rupee figures. Keep under 250 words.
"""

class MarketAgent(BaseAgent):
    def __init__(self):
        self.llm = LLMService()

    async def run(self, query: str, context: dict) -> dict:
        crops = context.get("crops", [])
        location = context.get("state", "India")

        # Fetch live prices from Agmarknet (data.gov.in free API)
        price_data = await self._fetch_prices(crops, location)

        response = self.llm.complete(MARKET_PROMPT.format(
            price_data=price_data,
            location=location,
            crops=", ".join(crops) if crops else "general crops",
            query=query,
        ))
        return {"response": response, "sources": ["Agmarknet (data.gov.in)"]}

    async def _fetch_prices(self, crops: list, state: str) -> str:
        if not crops:
            return "No specific crops in farmer profile. Showing general market info."
        try:
            url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            params = {
                "api-key": settings.DATA_GOV_IN_KEY or "579b464db66ec23bdd000001cdd3946e44ce4aad38034a291041822",
                "format": "json", "limit": 20,
                "filters[commodity]": crops[0].capitalize(),
            }
            if state and state != "India":
                params["filters[state]"] = state
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.get(url, params=params)
            records = resp.json().get("records", [])
            if not records:
                return f"No live price data found for {crops[0]} in {state}."
            lines = [f"Crop: {r.get('commodity','')} | Market: {r.get('market','')} ({r.get('district','')} {r.get('state','')}) | Modal: ₹{r.get('modal_price','')} | Date: {r.get('arrival_date','')}" for r in records[:10]]
            return "\n".join(lines)
        except Exception as e:
            return f"Could not fetch live prices: {e}. Advising based on general knowledge."
