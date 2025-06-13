from fastapi import APIRouter, Query, HTTPException, status
from app.schemas.hotel_schemas import HotelOffersResponse
from app.services.hotel_service import hotel_service
from datetime import date
from typing import Optional, List, Literal

router = APIRouter()

@router.get("/hotels/search", response_model=List[HotelOffersResponse])
def get_hotels(
    city_code: str = Query(..., min_length=3, max_length=3, description="IATA code of the destination city (e.g., 'PAR')."),
    check_in_date: date = Query(..., description="Check-in date of the stay in YYYY-MM-DD format."),
    check_out_date: date = Query(..., description="Check-out date in YYYY-MM-DD format."),
    num_adults: int = Query(1, ge=1, description="Number of adult guests per room. Defaults to 1."),
    num_rooms: int = Query(1, ge=1, description="Number of required rooms. Defaults to 1."),
    radius: Optional[int] = Query(None, gt=0, description="Maximum distance from the city in kilometers for initial hotel search."),
    chain_codes: Optional[List[str]] = Query(None, description="List of 2-capital-alphabet hotel chain codes (e.g., ['MC', 'HL'])."),
    ratings: Optional[List[Literal["1", "2", "3", "4", "5"]]] = Query(
        None, description="Hotel star ratings. Up to 5 values can be requested, e.g., ['4', '5']."
    ),
    currency: str = Query("USD", min_length=3, max_length=3, description="Desired currency code."),
    price_range: Optional[str] = Query(None, description="Desired price per night in interval (e.g., '200-300')."),
    best_rate_only: Optional[bool] = Query(None, description="True to return only the best available rate for each hotel."),
    max_hotels_to_search: Optional[int] = Query(5, ge=1, description="Maximum number of hotels to fetch detailed offers for.")
) -> List[HotelOffersResponse]:
    """
    Searches for hotels in a specified city and retrieves their detailed offers (prices, rooms).
    """
    hotel_offers = hotel_service.find_hotel_with_offers(
        city_code=city_code,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        num_adults=num_adults,
        num_rooms=num_rooms,
        radius=radius,
        chain_codes=chain_codes,
        ratings=ratings,
        currency=currency,
        price_range=price_range,
        best_rate_only=best_rate_only,
        max_hotels_to_search=max_hotels_to_search
    )

    if not hotel_offers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hotel offers found for city: '{city_code} with the given params."
        )

    return hotel_offers




   


