"""
Configuration settings for the Smart Renewable Energy Platform.
All API keys are loaded from environment variables - never hardcoded.
"""
import os
from dataclasses import dataclass

@dataclass
class Settings:
    # IBM Granite / WatsonX configuration
    GRANITE_API_KEY: str = os.environ.get("GRANITE_API_KEY", "")
    GRANITE_PROJECT_ID: str = os.environ.get("GRANITE_PROJECT_ID", "")
    GRANITE_API_URL: str = os.environ.get(
        "GRANITE_API_URL",
        "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation"
    )
    GRANITE_MODEL_ID: str = os.environ.get("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")

    # IBM Cloud configuration
    IBM_CLOUD_API_KEY: str = os.environ.get("IBM_CLOUD_API_KEY", "")
    IBM_CLOUD_REGION: str = os.environ.get("IBM_CLOUD_REGION", "us-south")

    # Weather API (optional external)
    WEATHER_API_KEY: str = os.environ.get("WEATHER_API_KEY", "")

    # App settings
    USE_MOCK_GRANITE: bool = os.environ.get("USE_MOCK_GRANITE", "true").lower() == "true"
    DEMO_MODE: bool = True
    APP_TITLE: str = "Smart Renewable Energy Intelligence Platform"
    APP_VERSION: str = "1.0.0-mvp"

    # Location data
    LOCATIONS: list = None

    def __post_init__(self):
        self.LOCATIONS = [
            {"id": "kutch", "name": "Kutch", "lat": 23.7337, "lon": 69.8597},
            {"id": "banaskantha", "name": "Banaskantha", "lat": 24.1742, "lon": 72.4378},
        ]
        # If no Granite API key is set, fall back to mock
        if not self.GRANITE_API_KEY:
            self.USE_MOCK_GRANITE = True


settings = Settings()
