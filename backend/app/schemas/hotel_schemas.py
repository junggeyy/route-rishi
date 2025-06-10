from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Literal

class HotelOffersSearchRequest(BaseModel):
    """
    Schema for hotel search request parameters.
    """
    hotel_ids: List[str] = Field(..., description="Amadeus property codes on 8 chars. Predefined list of hotel ids.")
    check_in_date: Optional[date] = Field(None, description="Check-in date of the stay in YYYY-MM-DD format. Defaults to today's date.")
    check_out_date: Optional[date] = Field(None, description="Check-out date in YYYY-MM-DD format. Defaults to check-in date +1.")
    num_adults: Optional[int]= Field(None, gt=0, description="Number of adult guests (must be at least 1). Defaults to 1.")
    num_rooms: Optional[int] = Field(None, gt=0, description="Number of required rooms. Defaults to 1.")
    currency: Optional[str] = Field("USD", min_length=3, max_length=3, description="Desired currency code.")
    price_range: Optional[str] = Field(None, description="Desired price per night in interval (e.g.,' 200-300').")
