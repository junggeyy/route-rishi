import requests
from typing import Optional, List, Literal
from datetime import date, datetime, timedelta
from app.core.config import settings
from app.schemas.hotel_schemas import (
    HotelListResponse,
    HotelOffersResponse,
    CityHotelInfo,
    DetailedHotelInfo,
    HotelOfferDetails,
    GeoCode,
    Distance,
    RoomInfo,
    GuestInfo,
    OfferPrice,
    RoomTypeEstimated,
    RoomDescription,
    CancellationPolicy
)

class AmadeusAuthError(Exception):
    """Custom exception for Amadeus authentication failures."""
    pass

class HotelService:
    """
    Service class to handle interactions with Amadeus Hotel APIs.
    """
    AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
    HOTEL_BY_CITY_API_URL = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    HOTEL_OFFERS_API_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"

    def __init__(self):
        self.api_key = settings.AMADEUS_API_KEY
        self.api_secret = settings.AMADEUS_API_SECRET
        self._access_token = None
        self._token_expires_at = None

    def _get_access_token(self) -> str:
        """
        Fetches a new Amadeus access token if current one is missing or expired.
        """
        if self._access_token and self._token_expires_at and datetime.now() < self._token_expires_at:
            return self._access_token # Token is still valid

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.api_secret
        }

        try:
            response = requests.post(self.AUTH_URL, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            auth_data = response.json()
            self._access_token = auth_data['access_token']
            # Amadeus returns expires_in in seconds
            expires_in = auth_data.get('expires_in', 3600) # Default to 1 hour if not specified
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60) # Subtract 60s buffer
            return self._access_token
        except requests.exceptions.RequestException as e:
            print(f"Amadeus authentication failed: {e}")
            raise AmadeusAuthError(f"Failed to get Amadeus access token: {e}")
        except KeyError as e:
            print(f"Amadeus authentication response missing key: {e}")
            raise AmadeusAuthError(f"Amadeus authentication response malformed: {e}")
    
    def get_hotels_by_city(
        self,
        city_code: str,
        radius: Optional[int] = None,
        chain_codes: Optional[List[str]] = None,
        ratings: Optional[List[Literal["1", "2", "3", "4", "5"]]] = None
    ) -> Optional[HotelListResponse]:
        """
        Calls Amadeus Hotels by City API to get a list of basic hotel information.
        """
        try:
            access_token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            params = {
                'cityCode': city_code.upper()
            }

            if radius is not None:
                params['radius'] = radius
            if chain_codes:
                params['chainCodes'] = ','.join(chain_codes)
            if ratings:
                params['ratings'] = ','.join(ratings)

            print(f"Amadeus Hotels by City URL: {self.HOTEL_BY_CITY_API_URL}?{requests.compat.urlencode(params)}")

            response = requests.get(self.HOTEL_BY_CITY_API_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("data"):
                print(f"No hotels found for city: {city_code}")
                return None
            
            hotels_list: List[CityHotelInfo] = []
            for hotel_data in data["data"]:
                geo_code = None
                if hotel_data.get("geoCode"):
                    geo_code = GeoCode(
                        latitude=hotel_data["geoCode"]["latitude"],
                        longitude=hotel_data["geoCode"]["longitude"]
                    )
                distance = None
                if hotel_data.get("distance"):
                    distance = Distance(
                        value=hotel_data["distance"]["value"],
                        unit=hotel_data["distance"]["unit"],
                    )
                country_code = hotel_data.get("address", {}).get("countryCode")

                hotels_list.append(CityHotelInfo(
                    hotel_id=hotel_data["hotelId"],
                    name=hotel_data["name"],
                    chain_code=hotel_data.get("chainCode"),
                    iata_code=hotel_data.get("iataCode"),
                    geo_code=geo_code,
                    country_code=country_code,
                    distance=distance
                ))
            return HotelListResponse(hotels=hotels_list)
        except AmadeusAuthError:
            raise # Re-raise auth errors immediately
        except requests.exceptions.RequestException as e:
            print(f"Amadeus 'Hotels by City' API call failed for {city_code}: {e}")
            return None
        except (KeyError, TypeError) as e:
            print(f"Error parsing Amadeus 'Hotels by City' response: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred in Amadeus Hotels_by_city: {e}")
            return None
        
    def get_hotel_offers(
        self,
        hotel_ids: List[str],
        check_in_date: date,
        check_out_date: date,
        num_adults: int,
        num_rooms: int,
        price_range: Optional[str],
        best_rate_only: Optional[bool],
        currency: str = "USD"
    )-> Optional[List[HotelOffersResponse]]:
        """
        Calls Amadeus Hotel Offers API to get detailed pricing and room information.
        This API returns offers per hotel ID.
        """
        if not hotel_ids:
            print("No hotel IDs provided for offers search.")
            return []

        all_offers_responses: List[HotelOffersResponse] = []

        try:
            access_token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            params = {
                'hotelIds': ','.join(hotel_ids),
                'checkInDate': check_in_date.isoformat(),
                'checkOutDate': check_out_date.isoformat(),
                'adults': num_adults,
                'roomQuantity': num_rooms,
                'currency': currency,
            }

            if price_range is not None:
                params['priceRange'] = price_range
            
            if best_rate_only is not None:
                params['bestRateOnly'] = best_rate_only
            
            ## add mappings for amenities later

            print(f"Amadeus Hotel Offers URL: {self.HOTEL_OFFERS_API_URL}?{requests.compat.urlencode(params)}")

            response = requests.get(self.HOTEL_OFFERS_API_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get("data"):
                print(f"No offers found for hotel IDs: {', '.join(hotel_ids)}")
                return None
            
            for hotel_offer_entry in data["data"]:
                hotel_info = DetailedHotelInfo(
                    hotel_id=hotel_offer_entry["hotel"]["hotelId"],
                    name=hotel_offer_entry["hotel"]["name"],
                    chain_code=hotel_offer_entry["hotel"].get("chainCode"),
                    city_code=hotel_offer_entry["hotel"].get("cityCode"),
                    latitude=hotel_offer_entry["hotel"].get("latitude"),
                    longitude=hotel_offer_entry["hotel"].get("longitude")
                )

                offers_list: List[HotelOfferDetails] = []
                for offer_data in hotel_offer_entry.get("offers", []):
                    room_info = None
                    if offer_data.get("room"):
                        room_info = RoomInfo(
                            type=offer_data["room"].get("type"),
                            type_estimated=RoomTypeEstimated(
                                category=offer_data["room"]["typeEstimated"].get("category"),
                                beds=offer_data["room"]["typeEstimated"].get("beds"),
                                bed_type=offer_data["room"]["typeEstimated"].get("bedType")
                            ) if offer_data["room"].get("typeEstimated") else None,
                            description=RoomDescription(
                                text=offer_data["room"]["description"].get("text"),
                                lang=offer_data["room"]["description"].get("lang")
                            ) if offer_data["room"].get("description") else None
                        )

                    guest_info = GuestInfo(adults=offer_data["guests"]["adults"])
                    
                    price_info = OfferPrice(
                        currency=offer_data["price"]["currency"],
                        total =float(offer_data["price"]["total"]),
                        base=float(offer_data["price"]["base"]) if offer_data["price"].get("base") 
                            else None
                    )

                    cancellation_policy = None
                    if offer_data.get("policies", {}).get("cancellation"):
                        cancellation_policy = CancellationPolicy(
                            type=offer_data["policies"]["cancellation"].get("type"),
                            description_text=offer_data["policies"]["cancellation"]["description"].get("text")
                        )

                    offers_list.append(HotelOfferDetails(
                        offer_id=offer_data["id"],
                        check_in_date=date.fromisoformat(offer_data["checkInDate"]),
                        check_out_date=date.fromisoformat(offer_data["checkOutDate"]),
                        guests=guest_info,
                        price=price_info,
                        room=room_info,
                        available=offer_data.get("available"),
                        payment_type=offer_data.get("policies", {}).get("paymentType"),
                        cancellation_policy=cancellation_policy
                    ))
                all_offers_responses.append(HotelOffersResponse(
                    hotel=hotel_info,
                    offers=offers_list
                ))
            return all_offers_responses
    
        except AmadeusAuthError:
            raise
        except requests.exceptions.RequestException as e:
            print(f"Amadeus 'Hotel Offers' API call failed for {hotel_ids}: {e}")
            return None
        except (KeyError, TypeError) as e:
            print(f"Error parsing Amadeus 'Hotel Offers' response: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred in get_hotel_offers: {e}")
            return None
        

    def find_hotel_with_offers(
        self,
        city_code: str,
        check_in_date: date,
        check_out_date: date,
        num_adults: int,
        num_rooms: int=1,
        radius: Optional[int]=None,
        chain_codes: Optional[List[str]] = None,
        ratings: Optional[List[Literal["1", "2", "3", "4", "5"]]] = None,
        currency: str = "USD",
        price_range: Optional[str] = None,
        best_rate_only: Optional[bool] = None,
        max_hotels_to_search: Optional[int] = 5
    ) -> List[HotelOffersResponse]:
        """
        Consolidated method to first search for hotels by city, then get their offers.
        Returns a list of HotelOffersResponse for each hotel found.
        """
        print(f"Searching for hotels in {city_code} from {check_in_date} to {check_out_date} for {num_adults} adults.")

        # Step 1: Search for hotels by city
        city_hotels_response = self.get_hotels_by_city(
            city_code=city_code,
            radius=radius,
            chain_codes=chain_codes,
            ratings=ratings
        )    

        if not city_hotels_response or not city_hotels_response.hotels:
            print(f"No hotels found in {city_code} for the initial search.")
            return []

        hotel_ids_for_offers = [
            hotel.hotel_id for hotel in city_hotels_response.hotels[:max_hotels_to_search]
        ]
        if not hotel_ids_for_offers:
            print("No hotel IDs available after initial city search.")
            return []
        
        print(f"Found {len(hotel_ids_for_offers)} hotels. Fetching offers for these hotels...")


        # Step 2: Get offers for the found hotel IDs
        hotel_offers_responses = self.get_hotel_offers(
            hotel_ids=hotel_ids_for_offers,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            num_adults=num_adults,
            num_rooms=num_rooms,
            currency=currency,
            price_range=price_range,
            best_rate_only=best_rate_only
        )

        if not hotel_offers_responses:
            print("No offers found for the selected hotels")
            return []
        
        return hotel_offers_responses
    
hotel_service = HotelService()