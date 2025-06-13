from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .api import router as api_router

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])

# Initialize the FastAPI app
app = FastAPI(
    title="AI Website Intelligence Agent",
    description="An API for extracting business insights from websites using AI.",
    version="1.0.0"
)

# Add state to the app for the limiter and handle rate limit exceptions
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# IMPORTANT: Remove the custom `rate_limit_middleware` if you are using
# `default_limits` on the Limiter object and adding the exception handler.
# The `slowapi` library will automatically apply the default limits to all routes
# if configured this way, and the exception handler will catch `RateLimitExceeded`.
# If you need per-route rate limiting, use `@limiter.limit("rate/time")` decorators
# on your individual route functions in `api.py`.

# Include the API router
app.include_router(api_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Website Intelligence Agent API. Visit /docs for documentation."}