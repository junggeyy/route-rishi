import os
import requests
from fastapi import APIRouter

router = APIRouter()
api_key = os.getenv("ExchangeRate_API_KEY")
url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'

@router.get("/currency/{code}")
def get_exchange_rate(code: str):
    """
    Retrieve the exchange rate of a country to USD.
    """
    response = requests.get(url)
    data = response.json()
    rate = data.get("conversion_rates", {}).get(code)

    return {"currency_code": code,
        "rate_to_usd": rate}

