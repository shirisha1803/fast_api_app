import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file>>
# This will load GEMINI_MODEL_NAME from your .env if it exists
load_dotenv(override=True)

class Settings(BaseSettings):
    """Manages application settings and environment variables."""
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "default_secret")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    # This line means: try to get GEMINI_MODEL_NAME from environment variables.
    # If not found, default to 'gemini-1.5-pro'.
    # When you set it in .env, os.getenv will pick it up.
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")

    class Config:
        env_file = ".env"

settings = Settings()

# ADD THIS LINE to see what model name is actually being loaded
print(f"DEBUG: GEMINI_MODEL_NAME loaded: {settings.GEMINI_MODEL_NAME}")