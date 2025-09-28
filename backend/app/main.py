import logging
import subprocess
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Run database migrations on startup (only in development)
if settings.DEBUG:
    try:
        logger.info("Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Database migrations completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Database migration failed: {e.stderr}")
        logger.warning("Continuing without migrations - database may not be up to date")
    except FileNotFoundError:
        logger.warning("Alembic not found - skipping migrations")

app = FastAPI(
    title="CStatSentry API",
    description="CS2 Anti-Cheat Detection System",
    version="1.0.0",
    redirect_slashes=False  # Disable automatic slash redirects
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "CStatSentry API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}