import requests
from typing import Optional, Dict, List, Any
from datetime import datetime
from urllib.parse import quote
from app.core.config import settings

class WeatherService:
    """
    Service class to handle interactions with the Tomorrow.io API.
    """
    BASE_URL = f"https://api.tomorrow.io/v4/weather/forecast?apikey={settings.TomorrowIO_API_KEY}"

    def get_weather_forecast(self, city: str, timesteps: str) -> Optional[Dict]:
        """
        Fetches the weather forecast of a target city within the next 5 days.

        Args:
            city (str): The name of the target city (eg: Paris).
            timesteps (str): Granularity of forecast: "1d" (daily) 
            or "1h" (hourly). Default is "1d".

        Returns:
            Optional[Dict]: Forecast summary with "signals", "raw",
            and "forecast_date" (which will be the start date of the average for 1d,
            or the specific hour for 1h).
        """
        try:
            encoded_city = quote(city)
            url = f"{self.BASE_URL}&location={encoded_city}&timesteps={timesteps}"
            response = requests.get(url, timeout=5)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            forecast_key = "daily" if timesteps == "1d" else "hourly"
            if not data["timelines"].get(forecast_key):
                print(f"[WeatherService Error] No '{forecast_key}' data found for {city} in API response.")
                return None
            
            forecast_entries = data["timelines"][forecast_key]

            if not forecast_entries:
                print(f"[WeatherService Error] No forecast entries found for {city} with timesteps '{timesteps}'.")
                return None

            if timesteps == "1d":
                # Calculate average for daily forecasts
                aggregated_values = self._aggregate_daily_forecasts(forecast_entries)
                # The forecast_date will be the time of the first entry
                forecast_date = forecast_entries[0]["time"]
                weather_data = aggregated_values
            else: # timesteps == "1h"
                # For hourly, we take the first entry
                forecast_data = forecast_entries[0]
                weather_data = forecast_data["values"]
                forecast_date = forecast_data["time"]

            summary = self.generate_weather_summary(weather_data)
            summary["forecast_date"] = forecast_date
            return summary

        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"[WeatherService Error] {e}")
            return None
    
    def _aggregate_daily_forecasts(self, daily_entries: List[Dict]) -> Dict:
        """
        Aggregates relevant weather metrics from multiple daily forecast entries.
        Calculates averages for temperature, wind, humidity, cloud cover, and sums for rain.
        """
        aggregated_values = {
            "temperatureAvg": [],
            "temperatureMax": [],
            "temperatureMin": [],
            "windSpeedAvg": [],
            "humidityAvg": [],
            "cloudCoverAvg": [],
            "uvIndexAvg": [],
            "precipitationSum": 0.0, # Accumulate total rain
            "rainAccumulationSum": 0.0, # Accumulate total rain accumulation
        }

        for entry in daily_entries:
            values = entry["values"]
            for key in ["temperatureAvg", "temperatureMax", "temperatureMin",
                        "windSpeedAvg", "humidityAvg", "cloudCoverAvg", "uvIndexAvg"]:
                if values.get(key) is not None:
                    aggregated_values[key].append(values[key])

            # Sum precipitation and rain accumulation
            aggregated_values["precipitationSum"] += values.get("precipitationSum", 0)
            aggregated_values["rainAccumulationSum"] += values.get("rainAccumulationSum", 0)


        # Calculate averages for collected lists
        final_averages = {}
        for key, value_list in aggregated_values.items():
            if isinstance(value_list, list) and value_list: # If it's a list and not empty
                final_averages[key] = sum(value_list) / len(value_list)
            elif not isinstance(value_list, list): # If it's a sum (like precipitationSum)
                final_averages[key] = value_list

        # Use rainAccumulationSum for precipitationSum
        final_averages["precipitationSum"] = final_averages.get("rainAccumulationSum", 0.0) 

        return final_averages

    @staticmethod  
    def generate_weather_summary(weather_data: Dict) -> Dict:
        """
        Converts raw weather data into qualitative labels.

        Args:
            weather_data (dict): Raw weather values from API.

        Returns:
            dict: {"signals": {...}, "raw": {...}}
        """
        def label_temp(celsius):
            if celsius is None: return "unavailable"
            if celsius < 5: return "cold"
            elif celsius < 15: return "cool"
            elif celsius < 25: return "warm"
            else: return "hot"

        def label_rain(mm):
            if mm is None: return "unavailable"
            if mm == 0: return "none"
            elif mm < 2: return "low"
            elif mm < 10: return "moderate"
            else: return "high"

        def label_wind(kph):
            if kph is None: return "unavailable"
            if kph < 10: return "calm"
            elif kph < 25: return "breezy"
            else: return "strong"

        def label_uv(uv):
            if uv is None: return "unavailable"
            if uv < 3: return "low"
            elif uv < 6: return "moderate"
            elif uv < 8: return "high"
            else: return "very_high"

        def label_humidity(h):
            if h is None: return "unavailable"
            if h < 30: return "dry"
            elif h < 60: return "moderate"
            else: return "humid"

        def label_clouds(cloud):
            if cloud is None: return "unavailable"
            if cloud < 10: return "clear"
            elif cloud < 40: return "partly_cloudy"
            elif cloud < 80: return "cloudy"
            else: return "overcast"

        # Raw values
        raw = {
            "temp_avg_c": weather_data.get("temperatureAvg"),
            "rain_mm": weather_data.get("precipitationSum", 0),
            "wind_kph": weather_data.get("windSpeedAvg"),
            "uv_index": weather_data.get("uvIndexAvg"),
            "humidity": weather_data.get("humidityAvg"),
            "cloud_cover": weather_data.get("cloudCoverAvg"),
        }

        signals = {
            "temp_avg": label_temp(raw["temp_avg_c"]),
            "rain_chance": label_rain(raw["rain_mm"]),
            "wind_speed": label_wind(raw["wind_kph"]),
            "uv_index": label_uv(raw["uv_index"]),
            "humidity": label_humidity(raw["humidity"]),
            "cloud_cover": label_clouds(raw["cloud_cover"]),
        }

        return {
            "signals": signals,
            "raw": raw
        }

weather_service = WeatherService()