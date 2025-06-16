import asyncio
from datetime import date, timedelta
from app.core.config import settings

from app.services.weather_service import weather_service
from app.services.currency_service import currency_service
from app.services.flight_service import flight_service
from app.services.hotel_service import hotel_service

async def test_services_directly():
    print("\n--- Testing Weather Service Directly ---")
    try:
        weather_data = weather_service.get_weather_forecast("New York", "1d")
        print(f"Weather Service Response: {weather_data}")
        if weather_data:
            print(f"Weather for {weather_data['city']} on {weather_data['forecast_date']}: {weather_data['signals']['temp_avg']}, {weather_data['signals']['cloud_cover']}")
        else:
            print("Weather service returned None.")
    except Exception as e:
        print(f"Error calling Weather Service: {e}")

    print("\n--- Testing Currency Service Directly ---")
    try:
        currency_rate = currency_service.get_exchange_rate_to_usd("JPY")
        print(f"Currency Service Response: {currency_rate}")
        if currency_rate:
            print(f"1 USD = {currency_rate} JPY")
        else:
            print("Currency service returned None.")
    except Exception as e:
        print(f"Error calling Currency Service: {e}")

    print("\n--- Testing Flight Service Directly ---")
    try:
        departure_date_test = date.today() + timedelta(days=30)
        return_date_test = date.today() + timedelta(days=35)
        flights_data = flight_service.search_flight_offers(
            origin_code="SFO",
            destination_code="LAX",
            departure_date=departure_date_test,
            num_adults=2,
            return_date=return_date_test
        )
        print(f"Flight Service Response: {flights_data}")
        if flights_data:
            for flight in flights_data:
                print(f"Flight ID: {flight.id}, Price: {flight.price_total} {flight.currency}")
        else:
            print("Flight service returned None.")
    except Exception as e:
        print(f"Error calling Flight Service: {e}")

    print("\n--- Testing Hotel Service Directly ---")
    try:
        check_in_date_test = date.today() + timedelta(days=60)
        check_out_date_test = date.today() + timedelta(days=65)
        hotels_data = hotel_service.find_hotels_with_offers(
            city_code="ROM",
            check_in_date=check_in_date_test,
            check_out_date=check_out_date_test,
            num_adults=1,
            ratings=['4']
        )
        print(f"Hotel Service Response: {hotels_data}")
        if hotels_data:
            for hotel_offers_response in hotels_data:
                hotel_name = hotel_offers_response.hotel.name
                for offer in hotel_offers_response.offers:
                    print(f"Hotel: {hotel_name}, Offer ID: {offer.offer_id}, Price: {offer.price.total} {offer.price.currency}")
        else:
            print("Hotel service returned None.")
    except Exception as e:
        print(f"Error calling Hotel Service: {e}")

if __name__ == "__main__":
    asyncio.run(test_services_directly())