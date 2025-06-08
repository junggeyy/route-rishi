from fastapi import APIRouter, HTTPException, status
from app.services.currency_service import currency_service
from app.schemas.currency_schemas import CurrencyRateResponse

router = APIRouter()

@router.get("/currency/{code}", response_model=CurrencyRateResponse)
def get_exchange_rate(code: str) -> CurrencyRateResponse:
    """
    Retrieve the exchange rate of a country to USD.
    The 'code' parameter represents the target currency (e.g., 'EUR', 'GBP').
    The response shows how many units of the target currency equal 1 USD.
    Example: If code='EUR' and rate_to_usd=0.92, it means 1 USD = 0.92 EUR.
    """
    rate = currency_service.get_exchange_rate_to_usd(code)

    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exchange rate for currency code '{code.upper()}' not found or could not be retrieved."
        )
    
    return CurrencyRateResponse(currency_code=code.upper(), rate_to_usd=rate)
