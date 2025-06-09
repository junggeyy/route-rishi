import re 
import requests
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta
from app.core.config import settings
from app.schemas.flight_schemas import FlightOffer, Itinerary, Segment


class AmadeusAuthError(Exception):
    """Custom exception for Amadeus authentication failures."""
    pass

class FlightService:
    """
    Service class to handle interactions with the Amadeus Flight Offers API.
    """
    AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
    API_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    
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
        
    def _parse_duration(self, duration_str: str) -> str:
        """
        Parses an ISO 8601 duration string (e.g., "PT13H56M") into a human-readable format.
        """
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            parts = []
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            return " ".join(parts) if parts else "0m"
        return duration_str # Return original if parsing fails
    
    def search_flight_offers(
        self,
        origin_code: str,
        destination_code: str,
        departure_date: date,
        num_adults: int,
        return_date: Optional[date] = None,
        num_children: Optional[int] = None,
        travel_class: Optional[str] = None,
        non_stop: Optional[bool] = None,
        max_price: Optional[int] = None,
        max_flights: Optional[int] = None,
        currency_code: str = "USD" # Default currency to USD
    ) -> Optional[List[FlightOffer]]:
        """
        Searches for flight offers using the Amadeus API.
        """
        try:
            access_token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            params = {
                'originLocationCode': origin_code.upper(),
                'destinationLocationCode': destination_code.upper(),
                'departureDate': departure_date.isoformat(),
                'adults': num_adults,
                'currencyCode': currency_code.upper()
            }

            if return_date:
                params['returnDate'] = return_date.isoformat()
            if num_children is not None and num_children > 0:
                params['children'] = num_children
            if travel_class:
                params['travelClass'] = travel_class
            if non_stop is not None: # Using `is not None` to handle False
                params['nonStop'] = non_stop
            if max_price:
                params['maxPrice'] = max_price
            if max_flights:
                params['max'] = max_flights # Amadeus uses 'max' for number of results

            print(f"Amadeus Flight Search URL: {self.API_URL}?{requests.compat.urlencode(params)}")

            response = requests.get(self.API_URL, headers=headers, params=params, timeout=15)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            data = response.json()

            if not data.get("data"):
                print("No flight offers found for the given criteria.")
                return None

            # Process the raw Amadeus response into the defined FlightOffer schema
            flight_offers_list: List[FlightOffer] = []
            for offer_data in data["data"]:
                itineraries = []
                for itin_data in offer_data["itineraries"]:
                    segments = []
                    for seg_data in itin_data["segments"]:
                        segments.append(Segment(
                            departure_airport_code=seg_data["departure"]["iataCode"],
                            departure_time=datetime.fromisoformat(seg_data["departure"]["at"]),
                            arrival_airport_code=seg_data["arrival"]["iataCode"],
                            arrival_time=datetime.fromisoformat(seg_data["arrival"]["at"]),
                            carrier_code=seg_data["carrierCode"],
                            flight_number=seg_data["number"],
                            duration=self._parse_duration(seg_data["duration"]),
                            number_of_stops=seg_data["numberOfStops"]
                        ))
                    itineraries.append(Itinerary(
                        duration=self._parse_duration(itin_data["duration"]),
                        segments=segments
                    ))

                flight_offers_list.append(FlightOffer(
                    id=offer_data["id"],
                    price_total=float(offer_data["price"]["grandTotal"]),
                    currency=offer_data["price"]["currency"],
                    itineraries=itineraries,
                    number_of_bookable_seats=offer_data.get("numberOfBookableSeats", 0), # Default if missing
                    last_ticketing_date=date.fromisoformat(offer_data["lastTicketingDate"]),
                    validating_airline_codes=offer_data.get("validatingAirlineCodes", [])
                ))
            return flight_offers_list
        
        except AmadeusAuthError as e:
            print(f"Authentication error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Amadeus API call failed: {e}")
            return None
        except (KeyError, TypeError) as e:
            print(f"Error parsing Amadeus response data: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred in flight service: {e}")
            return None
        
flight_service = FlightService()
