from fastapi import APIRouter
from dotenv import load_dotenv
from .endpoints import flights, currency, weather, hotels, chat, auth, itinerary

# Load all environment variables
load_dotenv()

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router)

# Tool routes
api_router.include_router(flights.router)
api_router.include_router(hotels.router)
api_router.include_router(weather.router)
api_router.include_router(currency.router)

# Chat routes 
api_router.include_router(chat.router)

# Itinerary routes
api_router.include_router(itinerary.router)