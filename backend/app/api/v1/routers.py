from fastapi import APIRouter
from .endpoints import flights
# hotels, attractions, weather, currency

api_router = APIRouter()

api_router.include_router(flights.router)
# api_router.include_router(flights.router)
# api_router.include_router(hotels.router)
# api_router.include_router(attractions.router)
# api_router.include_router(weather.router)
# api_router.include_router(currency.router)