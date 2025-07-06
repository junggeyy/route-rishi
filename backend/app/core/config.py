from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ExchangeRate_API_KEY: str
    TomorrowIO_API_KEY: str
    AMADEUS_API_KEY: str
    AMADEUS_API_SECRET: str
    GEMINI_API_KEY: str
    FIREBASE_SERVICE_ACCOUNT_KEY: str
    FIREBASE_WEB_API_KEY: str  

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
settings = Settings()