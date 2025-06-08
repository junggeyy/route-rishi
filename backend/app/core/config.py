from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ExchangeRate_API_KEY: str
    TomorrowIO_API_KEY: str

settings = Settings()