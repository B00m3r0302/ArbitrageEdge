"""Application configuration."""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings
    """
    model_config = ConfigDict(
        env_file = ".env",
        case_sensitive = True,
        env_file_encoding = "utf-8",
        extra="ignore"
    )

    project_name: str = "ArbitrageEngine"
    version: str = "0.1.0"
    description: str = "Odds Engine/API for calculating sports betting odds"
    api_v1_str: str = "/api/v1"

    debug: bool = False

    # rf token was not in here previously

settings = Settings()