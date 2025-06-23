from fastapi import APIRouter
from dotenv import load_dotenv
from .endpoints import flights, currency, weather, hotels, chat
# hotels, attractions, weather, currency

# Load all environment variables
load_dotenv()

api_router = APIRouter()

api_router.include_router(flights.router)
api_router.include_router(hotels.router)
api_router.include_router(weather.router)
api_router.include_router(currency.router)
api_router.include_router(chat.router)