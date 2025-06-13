from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from .config import settings

API_KEY_HEADER = APIKeyHeader(name="Authorization")

async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    """Validates the API key from the Authorization header."""
    if api_key_header == f"Bearer {settings.API_SECRET_KEY}":
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )