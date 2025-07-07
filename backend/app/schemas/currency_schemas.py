from pydantic import BaseModel, Field

class CurrencyRateResponse(BaseModel):
    """
    Schema for the response when retrieving a currency exchange rate.
    """
    currency_code: str = Field(..., description="The three-letter currency code (e.g., 'EUR', 'GBP').")
    rate_to_usd: str = Field(..., description="The exchange rate of the specified currency to 1 USD.")
