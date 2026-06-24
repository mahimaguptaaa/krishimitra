from agents.base_agent import BaseAgent
from services.weather_service import WeatherService, WeatherLocationError
from services.llm_service import LLMService

ADVISORY_PROMPT = """You are KrishiMitra's Weather Advisor.

Current Weather at {city}:
{current}

7-Day Forecast:
{forecast}

Farmer crops: {crops}
Question: {q}

Give ACTIONABLE farming advice based on weather. Format:
WEATHER SUMMARY: (1 line)
RECOMMENDATIONS: (3 bullet points with specific actions)
TIMING: When exactly to act (today/tomorrow/this week)

Be specific with days, quantities, crop names. Max 200 words.
"""

class WeatherAgent(BaseAgent):
    def __init__(self):
        self.ws = WeatherService()
        self.llm = LLMService()

    async def run(self, query: str, context: dict) -> dict:
        city = context.get("state") or context.get("city") or "Delhi"
        try:
            current = await self.ws.get_current(city)
            forecast = await self.ws.get_forecast(city)
        except WeatherLocationError:
            # FIX #6: friendly message instead of a raw exception leaking
            # into the chat (was showing "...नहीं मिल सका: 'main'").
            return {
                "response": (
                    f'I could not find weather data for "{city}". '
                    f"Could you tell me the name of a bigger nearby town, "
                    f"or your district name? For example: Kanpur, Lucknow, Ludhiana."
                ),
                "sources": [],
            }
        except Exception:
            return {
                "response": "Weather service is temporarily unavailable. Please try again in a moment.",
                "sources": [],
            }

        forecast_text = "\n".join(
            f"  {d['date']}: {d['temp_min']}-{d['temp_max']}C rain:{d['rain_mm']}mm {d['description']}"
            for d in forecast
        )
        current_text = f"Temp:{current['temperature']}C Humidity:{current['humidity']}% Wind:{current['wind_speed']}m/s {current['description']}"

        r = self.llm.complete(ADVISORY_PROMPT.format(
            city=current["city"], current=current_text, forecast=forecast_text,
            crops=", ".join(context.get("crops", []) or ["crops"]), q=query,
        ))
        return {"response": r, "sources": ["OpenWeatherMap"], "metadata": {"current": current, "forecast": forecast}}
