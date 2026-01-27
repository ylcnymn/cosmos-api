"""
Configuration settings for CosmosAPI (Pydantic v2 compatible)
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application configuration"""
    
    # Server settings
    APP_NAME: str = "CosmosAPI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "NASA JPL data-based real-time astronomical calculation service"
    
    # API settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)