"""FastAPI main application."""

import logging

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, messages, users, websocket
from app.core.config import settings
from app.core.rate_limiter import RateLimiter, rate_limiter
from app.services.presence_service import PresenceService, presence_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready realtime chat backend with FastAPI, WebSockets, PostgreSQL, and Redis",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "https://lllglobalchat.netlify.app",
        "*",  # Remove in production for security
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Redis client
redis_client: redis.Redis = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    global redis_client, rate_limiter, presence_service

    logger.info("Starting up application...")

    # Initialize Redis client
    redis_url = settings.REDIS_URL.strip()
    if not redis_url.startswith(("redis://", "rediss://", "unix://")):
        logger.error(
            f"Invalid REDIS_URL format. It must start with 'redis://' or 'rediss://'. Current value: {redis_url[:10]}..."
        )
        # Provide a dummy client or raise a more helpful error
        raise ValueError(
            f"REDIS_URL must start with 'redis://' or 'rediss://'. Please check your Render Environment variables."
        )

    redis_client = redis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=False,
    )

    # Test Redis connection
    try:
        await redis_client.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise

    # Initialize rate limiter
    import app.core.rate_limiter as rl_module

    rl_module.rate_limiter = RateLimiter(redis_client)
    logger.info("Rate limiter initialized")

    # Initialize presence service
    import app.services.presence_service as ps_module

    ps_module.presence_service = PresenceService(redis_client)
    logger.info("Presence service initialized")

    # Initialize OTP service
    import app.services.otp_service as otp_module
    from app.services.otp_service import OTPService

    otp_module.otp_service = OTPService(redis_client)
    logger.info("OTP service initialized")

    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    global redis_client

    logger.info("Shutting down application...")

    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

    logger.info("Application shutdown complete")


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Get the path to the frontend directory
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(websocket.router)

# Serve static files from the frontend directory
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/")
async def root():
    """Serve the frontend index.html at the root path."""
    return FileResponse(os.path.join(frontend_path, "index.html"))


# Add a catch-all to serve the frontend for any other GET requests (for SPA routing if needed)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Only serve the frontend if the path doesn't start with common API prefixes
    if full_path.split("/")[0] not in [
        "auth",
        "users",
        "messages",
        "ws",
        "docs",
        "redoc",
        "openapi.json",
        "static",
    ]:
        return FileResponse(os.path.join(frontend_path, "index.html"))
