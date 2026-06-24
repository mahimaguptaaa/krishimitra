from fastapi import APIRouter, Depends, Query
from middleware.auth_middleware import get_current_user
from services.weather_service import WeatherService

router = APIRouter()
weather_svc = WeatherService()

@router.get("/current")
async def current_weather(
    city: str = Query(default="Delhi"),
    user_id: str = Depends(get_current_user)
):
    data = await weather_svc.get_current(city)
    return data

@router.get("/forecast")
async def forecast(
    city: str = Query(default="Delhi"),
    user_id: str = Depends(get_current_user)
):
    data = await weather_svc.get_forecast(city)
    return {"city": city, "forecast": data}
