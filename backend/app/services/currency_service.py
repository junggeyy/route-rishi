import requests
from typing import Optional
from app.core.config import settings

class CurrencyService:
    """
    Service class to handle interactions with the ExchangeRate-API.
    """
    BASE_URL = f"https://v6.exchangerate-api.com/v6/{settings.ExchangeRate_API_KEY}"


    def get_exchange_rate_to_usd(self, target_currency_code: str) -> str:
        """
        Fetches the exchange rate of a target currency to USD.
        Assumes the base currency for the API call is USD.

        Args:
            target_currency_code (str): The three-letter code of the target currency (e.g., 'EUR').

        Returns:
            Optional[float]: The exchange rate of the target currency to 1 USD,
                             or None if the currency code is invalid or API call fails.
        """
        try:
            url = f"{self.BASE_URL}/latest/USD"
            response = requests.get(url, timeout=5)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            data = response.json()
            if data.get("result") == "success":
                rate = data.get("conversion_rates", {}).get(target_currency_code.upper())
                return f"The current exchange rate for {target_currency_code} is {rate}."
            else:
                print(f"Error from ExchangeRate-API: {data.get('error-type')}")
                return None
            
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"[CurrencyService Error] {e}")
            return None

currency_service = CurrencyService()