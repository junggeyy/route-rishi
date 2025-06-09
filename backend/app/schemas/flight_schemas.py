from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Literal

class FlightSearchRequest(BaseModel):
    """
    Schema for flight search request parameters.
    """
    origin_code: str = Field(..., min_length=3, max_length=3, description="IATA code of the origin airport (e.g., 'CVG').")
    destination_code: str = Field(..., min_length=3, max_length=3, description="IATA code of the destination airport (e.g., 'JFK').")
    departure_date: date = Field(..., description="Departure date in YYYY-MM-DD format.")
    num_adults: int = Field(..., gt=0, description="Number of adult travelers (must be at least 1).")
    return_date: Optional[date] = Field(None, description="Return date in YYYY-MM-DD format (required for two-way flights).")
    num_children: Optional[int] = Field(None, ge=0, description="Number of child travelers.")
    travel_class: Optional[Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]] = Field(
        None, description="Preferred travel class."
    )
    non_stop: Optional[bool] = Field(None, description="True if only non-stop flights are desired.")
    max_price: Optional[int] = Field(None, gt=0, description="Maximum desired price for the flight.")
    max_flights: Optional[int] = Field(5, ge=1, le=20, description="Maximum number of flight offers to return (default is 5).")

class Segment(BaseModel):
    """
    Schema for a flight segment (one leg of a journey).
    """
    departure_airport_code: str
    departure_time: datetime
    arrival_airport_code: str
    arrival_time: datetime
    carrier_code: str
    flight_number: str
    duration: str # e.g., "PT2H14M"
    number_of_stops: int # Calculated from segments

class Itinerary(BaseModel):
    """
    Schema for a complete flight itinerary (e.g., outbound or inbound journey).
    """
    duration: str # Total duration of the itinerary
    segments: List[Segment]

class FlightOffer(BaseModel):
    """
    Schema for a single flight offer.
    """
    id: str
    price_total: float
    currency: str
    itineraries: List[Itinerary]
    number_of_bookable_seats: int
    last_ticketing_date: date
    validating_airline_codes: List[str]


class FlightSearchResponse(BaseModel):
    """
    Schema for the overall flight search response.
    """
    flight_offers: List[FlightOffer]