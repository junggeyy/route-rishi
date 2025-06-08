from fastapi import APIRouter, HTTPException, status, Query
from app.services.weather_service import weather_service
from app.schemas.weather_schemas import WeatherForecastResponse
from typing import Literal

router = APIRouter()

@router.get("/forecast/{city}", response_model=WeatherForecastResponse)
def get_weather_forecast(
    city: str,
    timesteps: Literal["1d", "1h"]= Query("1d")
) -> WeatherForecastResponse:
    """
    Retrieve weather forecast with raw data & signal values for
    a target city.
    """
    summary_data = weather_service.get_weather_forecast(city, timesteps)

    if summary_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Forecast for for city: '{city}' not found or could not be retrieved."
        )
    
    return WeatherForecastResponse(
        city=city,
        forecast_date=summary_data["forecast_date"],
        timesteps=timesteps,
        signals=summary_data["signals"],
        raw=summary_data["raw"]
    )