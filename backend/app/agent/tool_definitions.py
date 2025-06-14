from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional, Literal

from app.services.weather_service import weather_service
from app.services.currency_service import currency_service
from app.services.flight_service import flight_service
from app.services.hotel_service import hotel_service

from app.schemas.weather_schemas import WeatherForecastResponse
from app.schemas.currency_schemas import CurrencyRateResponse
from app.schemas.flight_schemas import FlightSearchRequest
from app.schemas.hotel_schemas import HotelSearchByCityRequest, HotelOffersSearchRequest

# --- Weather Tool ---
class WeatherToolInput(BaseModel):
    city: str = Field(description="The name of the target city (e.g., 'Paris', 'New York').")
    timesteps: Literal["1d", "1h"] = Field("1d", description="Granularity of forecast: '1d' (daily) or '1h' (hourly). Default is '1d'.")

weather_tool = StructuredTool.from_function(
    func=weather_service.get_weather_forecast,
    name="get_weather_forecast",
    description="Useful for retrieving weather forecasts for a specified city. "
                "Provides a summary including temperature, rain, wind, UV index, humidity, and cloud cover. "
                "Timesteps can be '1d' for daily average or '1h' for hourly forecast. "
                "Example: 'What's the weather in London tomorrow?' or 'Tell me the hourly forecast for Tokyo.'",
    args_schema=WeatherToolInput,
    verbose=True # on for debugging
)

# --- Currency Tool ---
class CurrencyToolInput(BaseModel):
    code: str = Field(description="The three-letter currency code (e.g., 'EUR', 'GBP', 'JPY') to get its exchange rate to USD.")

currency_tool = StructuredTool.from_function(
    func=currency_service.get_exchange_rate_to_usd,
    name="get_exchange_rate",
    description="Useful for retrieving the exchange rate of a specific currency to US Dollars. "
                "Input should be a 3-letter currency code like 'EUR' or 'JPY'. "
                "Example: 'How much is 1 USD in Euros?' or 'What is the exchange rate for JPY?'",
    args_schema=CurrencyToolInput,
    verbose=True
)

# --- Flight Tool ---
flight_tool = StructuredTool.from_function(
    func=flight_service.search_flight_offers,
    name="search_flight_offers",
    description="""Useful for finding flight options between two cities.
                Requires origin and destination IATA codes (e.g., 'JFK', 'CDG'), departure date, and number of adults.
                Can optionally include return date for round trips, number of children, travel class,
                whether to search for non-stop flights only, a maximum price, and the maximum number of results.
                Example queries:
                - 'Find flights from New York to London for 2 adults departing next month.'
                - 'Search for non-stop economy flights from SFO to Tokyo for one person departing 2025-07-15 and returning 2025-07-22, maximum $1000.'
                - 'What's the cheapest one-way flight from Boston to Miami for 3 adults on 2025-08-01?'
                """,
    args_schema=FlightSearchRequest,
    verbose=True
)

# --- Hotel Tools ---
class HotelToolInput(BaseModel):
    city_code: str = Field(min_length=3, max_length=3, description="The IATA city code for the hotel search (e.g., 'PAR', 'LON').")
    check_in_date: date = Field(description="The check-in date for the hotel stay in YYYY-MM-DD format.")
    check_out_date: date = Field(description="The check-out date for the hotel stay in YYYY-MM-DD format.")
    num_adults: int = Field(ge=1, description="The number of adult guests per room (must be at least 1).")
    num_rooms: int = Field(1, ge=1, description="The number of rooms required. Default is 1.")
    radius: Optional[int] = Field(None, gt=0, description="Optional. Maximum distance from the city center in kilometers to search for hotels.")
    chain_codes: Optional[List[str]] = Field(None, description="Optional. List of 2-capital-alphabet hotel chain codes (e.g., ['MC', 'HL']) to filter results.")
    ratings: Optional[List[Literal["1", "2", "3", "4", "5"]]] = Field(
        None, description="Optional. Hotel star ratings to filter by, e.g., ['4', '5']."
    )
    currency: str = Field("USD", min_length=3, max_length=3, description="Optional. Desired currency code for prices. Default is 'USD'.")
    price_range: Optional[str] = Field(None, description="Optional. Desired total price for the stay in an interval format (e.g., '200-500').")
    best_rate_only: Optional[bool] = Field(None, description="Optional. Set to true to return only the best available rate for each hotel. Default is false if omitted.")
    max_hotels_to_search: Optional[int] = Field(5, ge=1, description="Optional. Maximum number of hotels to fetch detailed offers for (from the initial city search). Default is 5.")
    

hotel_tool = StructuredTool.from_function(
    func=hotel_service.find_hotels_with_offers,
    name="find_hotels_with_offers",
    description="""Useful for searching for hotels in a specific city and getting detailed offers including prices and room information.
                Requires a city IATA code, check-in date, check-out date, and number of adult guests.
                Can optionally filter by radius, hotel chain codes, star ratings, currency, price range,
                whether to get only the best rate, maximum number of hotels to search, and preferred amenities.
                Example queries:
                - 'Find a hotel in Paris for 2 adults checking in on 2025-07-01 and checking out on 2025-07-05.'
                - 'Search for a 4 or 5-star hotel in London with a swimming pool, for 1 adult from tomorrow for 3 nights, maximum $500 total.'
                - 'Are there any hotels in Tokyo with Wi-Fi available for 2 rooms, 4 adults total, next weekend?'
                """,
    args_schema=HotelToolInput,
    verbose=True
)

# Combine all tools
all_tools = [weather_tool, currency_tool, flight_tool, hotel_tool]