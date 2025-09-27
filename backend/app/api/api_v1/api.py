from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, players, matches, dashboard, dev
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Include development endpoints only in debug mode
if settings.DEBUG:
    api_router.include_router(dev.router, prefix="/dev", tags=["development"])