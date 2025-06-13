from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Literal

class HotelOffersSearchRequest(BaseModel):
    """
    Schema for multiple hotel offers search request parameters.
    """
    hotel_ids: List[str] = Field(..., description="Amadeus property codes on 8 chars. Predefined list of hotel ids.")
    check_in_date: date = Field(..., description="Check-in date of the stay in YYYY-MM-DD format. Defaults to today's date.")
    check_out_date: date = Field(..., description="Check-out date in YYYY-MM-DD format. Defaults to check-in date +1.")
    num_adults: int= Field(..., gt=0, description="Number of adult guests (must be at least 1). Defaults to 1.")
    num_rooms: Optional[int] = Field(1, gt=0, description="Number of required rooms. Defaults to 1.")
    currency: Optional[str] = Field("USD", min_length=3, max_length=3, description="Desired currency code. Required if using priceRange.")
    price_range: Optional[str] = Field(None, description="Desired price per night in interval (e.g.,' 200-300').")
    best_rate_only: Optional[bool] = Field(None, description="Use to return only the cheapest offer. Deaults to True.")
    ## need to add ammenities 


class HotelSearchByCityRequest(BaseModel):
    """
    Schema for hotel search in a city request parameters. 
    """
    city_code: str = Field(..., min_length=3, max_length=3, description="IATA code of the destinaton city (e.g., 'PAR').")
    radius: Optional[int] = Field(5, gt=0, description="Maximum distance from the city in kilometers")
    chain_codes: Optional[List[str]] = Field(None, description="List of hotel chain codes, consiting of 2 capital alphabets")
    ratings: Optional[List[Literal["1", "2", "3", "4", "5"]]] = Field(None, description=
                                    "Hotel stars. Upto 4 values can be request at once, comma seperated")
    

# --- Schemas for HotelListResponse (from hotels/by-city) ---
class GeoCode(BaseModel):
    latitude: float
    longitude: float

class Distance(BaseModel):
    value: float
    unit: str

class CityHotelInfo(BaseModel):
    """
    Essential information for a single hotel found by city search.
    """
    hotel_id: str = Field(..., description="Unique 8-character Amadeus hotel ID.")
    name: str = Field(..., description="Name of the hotel.")
    chain_code: Optional[str] = Field(None, description="Hotel chain code (e.g., 'MC' for Marriott).")
    iata_code: Optional[str] = Field(None, description="IATA city code the hotel is located in.")
    geo_code: Optional[GeoCode] = Field(None, description="Geographical coordinates of the hotel.")
    # Address field from Amadeus often includes just countryCode in this response.
    # If more is needed, it must be extracted or filled from Hotel Offers API.
    country_code: Optional[str] = Field(None, description="Country code of the hotel's address.")
    distance: Optional[Distance] = Field(None, description="Distance from the searched city point.")

class HotelListResponse(BaseModel):
    """
    Overall response for a hotel search by city, returning a list of basic hotel info.
    """
    hotels: List[CityHotelInfo] = Field(..., description="List of hotels found in the specified city.")


# --- Schemas for HotelOffersResponse (from hotel-offers) ---

class RoomTypeEstimated(BaseModel):
    """
    Estimated room type details.
    """
    category: Optional[str] = Field(None, description="e.g., 'EXECUTIVE_ROOM', 'STANDARD_ROOM'.")
    beds: Optional[int] = Field(None, description="Number of beds in the room.")
    bed_type: Optional[str] = Field(None, description="Type of bed, e.g., 'KING', 'DOUBLE'.")

class RoomDescription(BaseModel):
    """
    Description of the room.
    """
    text: Optional[str] = Field(None, description="Full description of the room.")
    lang: Optional[str] = Field(None, description="Language of the description (e.g., 'EN').")

class RoomInfo(BaseModel):
    """
    Combined room details within an offer.
    """
    type: Optional[str] = Field(None, description="Internal room type code.")
    type_estimated: Optional[RoomTypeEstimated] = Field(None, description="Estimated room category and bed details.")
    description: Optional[RoomDescription] = Field(None, description="Detailed room description.")

class GuestInfo(BaseModel):
    """
    Guest details for the offer.
    """
    adults: int = Field(..., description="Number of adults included in the offer.")

class OfferPrice(BaseModel):
    """
    Price details for a specific hotel offer.
    """
    currency: str = Field(..., description="Currency of the total price (e.g., 'GBP', 'USD').")
    total: float = Field(..., description="Total price for the offer.")
    base: Optional[float] = Field(None, description="Base price before taxes/fees.")

class CancellationPolicy(BaseModel):
    """
    Cancellation policy details.
    """
    type: Optional[str] = Field(None, description="Type of cancellation, e.g., 'FULL_STAY'.")
    description_text: Optional[str] = Field(None, alias="description.text", description="Description of the cancellation policy.") # Uses alias to flatten nested key

class HotelOfferDetails(BaseModel):
    """
    Schema for a single detailed hotel offer (from /hotel-offers).
    """
    offer_id: str = Field(..., description="Unique identifier for this specific offer.")
    check_in_date: date = Field(..., description="Check-in date for this offer.")
    check_out_date: date = Field(..., description="Check-out date for this offer.")
    guests: GuestInfo = Field(..., description="Guest details for the offer.")
    price: OfferPrice = Field(..., description="Price details for the hotel offer.")
    room: Optional[RoomInfo] = Field(None, description="Details about the specific room type offered.")
    available: Optional[bool] = Field(None, description="True if the offer is currently available.")
    payment_type: Optional[str] = Field(None, alias="policies.paymentType", description="Type of payment policy (e.g., 'deposit', 'guarantee').") # Uses alias to flatten nested key
    cancellation_policy: Optional[CancellationPolicy] = Field(None, alias="policies.cancellation", description="Details of the cancellation policy.") # Uses alias to flatten nested key

class DetailedHotelInfo(BaseModel):
    """
    Information about the hotel associated with the detailed offers.
    This comes directly nested in the /hotel-offers response.
    """
    hotel_id: str = Field(..., description="Unique 8-character Amadeus hotel ID.")
    name: str = Field(..., description="Name of the hotel.")
    chain_code: Optional[str] = None
    city_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class HotelOffersResponse(BaseModel):
    """
    Overall response for detailed hotel offers for a specific hotel (or hotels).
    """
    hotel: DetailedHotelInfo = Field(..., description="Information about the hotel for which offers are returned.")
    offers: List[HotelOfferDetails] = Field(..., description="List of detailed offers for the hotel.")
