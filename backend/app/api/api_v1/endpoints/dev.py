from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.crud.user import get_user_by_steam_id, create_user
from datetime import timedelta

router = APIRouter()


@router.post("/toggle-dev-mode")
async def toggle_dev_mode() -> Dict[str, Any]:
    """Toggle development mode (for testing only)"""
    # Note: In a real app, this would be controlled by environment variables
    # This is just for demonstration
    return {
        "dev_mode": settings.DEV_MODE,
        "message": f"Development mode is {'enabled' if settings.DEV_MODE else 'disabled'}"
    }


@router.post("/login")
async def dev_login(
    db: Session = Depends(get_db)
) -> Token:
    """Development login - creates a token for testing without Steam"""
    if not settings.DEV_MODE:
        return {"error": "Development mode not enabled"}

    # Create or get development user
    dev_steam_id = "76561197960287930"
    user = get_user_by_steam_id(db, steam_id=dev_steam_id)
    if user is None:
        user_data = {
            "steam_id": dev_steam_id,
            "steam_name": "Dev User",
            "avatar_url": "https://via.placeholder.com/184x184.png?text=Dev"
        }
        user = create_user(db, user_data)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=dev_steam_id, expires_delta=access_token_expires
    )

    return Token(access_token=access_token)


@router.get("/status")
async def dev_status() -> Dict[str, Any]:
    """Get development environment status"""
    return {
        "dev_mode": settings.DEV_MODE,
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "database_url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "configured",
        "redis_url": settings.REDIS_URL
    }