# app/schemas/weather_schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

# --- Sub-schemas for WeatherForecastResponse ---

class WeatherSignals(BaseModel):
    """
    Qualitative labels for various weather conditions.
    """
    temp_avg: Literal["cold", "cool", "warm", "hot"] = Field(..., description="Average temperature category.")
    rain_chance: Literal["none", "low", "moderate", "high"] = Field(..., description="Rainfall amount category.")
    wind_speed: Literal["calm", "breezy", "strong"] = Field(..., description="Wind speed category.")
    uv_index: Literal["low", "moderate", "high", "very_high"] = Field(..., description="UV Index category.")
    humidity: Literal["dry", "moderate", "humid"] = Field(..., description="Humidity category.")
    cloud_cover: Literal["clear", "partly_cloudy", "cloudy", "overcast"] = Field(..., description="Cloud cover category.")

class RawWeatherValues(BaseModel):
    """
    Raw numerical values for various weather metrics.
    """
    temp_avg_c: Optional[float] = Field(None, description="Average temperature in Celsius.")
    rain_mm: Optional[float] = Field(None, description="Total precipitation in millimeters.")
    wind_kph: Optional[float] = Field(None, description="Average wind speed in kilometers per hour.")
    uv_index: Optional[float] = Field(None, description="Average UV Index.")
    humidity: Optional[float] = Field(None, description="Average humidity percentage.")
    cloud_cover: Optional[float] = Field(None, description="Average cloud cover percentage.")

# --- Main Weather Forecast Response Schema ---

class WeatherForecastResponse(BaseModel):
    """
    Schema for the weather forecast response, combining signals and raw data.
    """
    city: str = Field(..., description="The name of the city for which the forecast is provided.")
    forecast_date: datetime = Field(..., description="The date of the weather forecast in ISO 8601 format.")
    timesteps: Literal["1d", "1h"] = Field(..., description="Granularity of the forecast ('1d' for daily, '1h' for hourly).")
    signals: WeatherSignals = Field(..., description="Qualitative labels summarizing weather conditions.")
    raw: RawWeatherValues = Field(..., description="Raw numerical weather data.")
