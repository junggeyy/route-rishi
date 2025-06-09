from fastapi import APIRouter, Query, HTTPException, status
from app.schemas.flight_schemas import FlightSearchRequest, FlightSearchResponse
from app.services.flight_service import flight_service
from typing import Optional, Literal
from datetime import date

router = APIRouter()

@router.get("/flights/search", response_model=FlightSearchResponse)
def get_flights(
    origin_code: str = Query(..., min_length=3, max_length=3, description="IATA code of the origin airport (e.g., 'CVG')."),
    destination_code: str = Query(..., min_length=3, max_length=3, description="IATA code of the destination airport (e.g., 'JFK')."),
    departure_date: date = Query(..., description="Departure date in YYYY-MM-DD format."),
    num_adults: int = Query(..., gt=0, description="Number of adult travelers (must be at least 1)."),
    return_date: Optional[date] = Query(None, description="Return date in YYYY-MM-DD format (required for two-way flights)."),
    num_children: Optional[int] = Query(None, ge=0, description="Number of child travelers."),
    travel_class: Optional[Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]] = Query(
        None, description="Preferred travel class."
    ),
    non_stop: Optional[bool] = Query(None, description="True if only non-stop flights are desired."),
    max_price: Optional[int] = Query(None, gt=0, description="Maximum desired price for the flight."),
    max_flights: Optional[int] = Query(5, ge=1, le=20, description="Maximum number of flight offers to return (default is 5)."),
) -> FlightSearchResponse:
    """
    Retrieve flight information based on the provided criteria.
    """
    flight_offers = flight_service.search_flight_offers(
        origin_code=origin_code,
        destination_code=destination_code,
        departure_date=departure_date,
        num_adults=num_adults,
        return_date=return_date,
        num_children=num_children,
        travel_class=travel_class,
        non_stop=non_stop,
        max_price=max_price,
        max_flights=max_flights
    )

    if not flight_offers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No flight offers found matching your criteria."
        )

    return FlightSearchResponse(flight_offers=flight_offers)
