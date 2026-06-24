import httpx
from config import settings

# Fallback so the farmer always gets SOMETHING useful even if their
# village/town isn't in OpenWeatherMap's geocoding database.
STATE_CAPITALS = {
    "uttar pradesh": "Lucknow", "up": "Lucknow",
    "punjab": "Chandigarh", "maharashtra": "Mumbai", "bihar": "Patna",
    "rajasthan": "Jaipur", "gujarat": "Ahmedabad", "madhya pradesh": "Bhopal",
    "west bengal": "Kolkata", "karnataka": "Bengaluru", "tamil nadu": "Chennai",
    "andhra pradesh": "Amaravati", "telangana": "Hyderabad", "haryana": "Chandigarh",
    "kerala": "Thiruvananthapuram", "odisha": "Bhubaneswar", "assam": "Guwahati",
}

class WeatherLocationError(Exception):
    """Raised when no usable location could be resolved at all."""
    pass

class WeatherService:
    BASE = "https://api.openweathermap.org/data/2.5"
    GEO = "https://api.openweathermap.org/geo/1.0/direct"

    async def _geocode(self, query: str):
        """Try to resolve a (possibly messy) place string to lat/lon."""
        candidates = []
        clean = query.split(",")[0].strip()  # "Kanpur, Uttar Pradesh" -> "Kanpur"
        if clean:
            candidates.append(f"{clean},IN")
            candidates.append(clean)
        if query.strip() and query.strip() != clean:
            candidates.append(query.strip())

        async with httpx.AsyncClient(timeout=8) as client:
            for q in candidates:
                try:
                    r = await client.get(self.GEO, params={"q": q, "limit": 1, "appid": settings.OPENWEATHER_KEY})
                    data = r.json()
                    if data:
                        d = data[0]
                        return d["lat"], d["lon"], d.get("name", clean), d.get("state", "")
                except Exception:
                    continue

        # Last resort: try matching a known state name to its capital
        lower = query.lower()
        for state, capital in STATE_CAPITALS.items():
            if state in lower:
                async with httpx.AsyncClient(timeout=8) as client:
                    r = await client.get(self.GEO, params={"q": f"{capital},IN", "limit": 1, "appid": settings.OPENWEATHER_KEY})
                    data = r.json()
                    if data:
                        d = data[0]
                        return d["lat"], d["lon"], f"{capital} (near {query})", d.get("state", "")
        return None

    async def get_current(self, city: str) -> dict:
        geo = await self._geocode(city)
        if not geo:
            raise WeatherLocationError(f"Could not find weather data for '{city}'. Try a nearby bigger town or your district name.")
        lat, lon, resolved_name, state = geo

        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{self.BASE}/weather", params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_KEY, "units": "metric"})
        d = r.json()
        if "main" not in d:
            raise WeatherLocationError(f"Weather data unavailable for '{city}' right now. Please try again shortly.")

        return {
            "city": resolved_name,
            "temperature": d["main"]["temp"],
            "feels_like": d["main"]["feels_like"],
            "humidity": d["main"]["humidity"],
            "description": d["weather"][0]["description"],
            "wind_speed": d["wind"]["speed"],
        }

    async def get_forecast(self, city: str) -> list:
        geo = await self._geocode(city)
        if not geo:
            raise WeatherLocationError(f"Could not find forecast for '{city}'. Try a nearby bigger town or your district name.")
        lat, lon, resolved_name, state = geo

        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{self.BASE}/forecast", params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_KEY, "units": "metric", "cnt": 40})
        items = r.json().get("list", [])
        if not items:
            raise WeatherLocationError(f"Forecast unavailable for '{city}' right now.")

        from collections import defaultdict
        days: dict = defaultdict(list)
        for item in items:
            date = item["dt_txt"].split(" ")[0]
            days[date].append(item)
        result = []
        for date, entries in sorted(days.items()):
            temps = [e["main"]["temp"] for e in entries]
            rain = sum(e.get("rain", {}).get("3h", 0) for e in entries)
            result.append({
                "date": date,
                "temp_min": round(min(temps), 1),
                "temp_max": round(max(temps), 1),
                "rain_mm": round(rain, 2),
                "description": entries[len(entries)//2]["weather"][0]["description"],
            })
        return result[:7]
