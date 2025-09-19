from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="CStatSentry API",
    description="CS2 Anti-Cheat Detection System",
    version="1.0.0"
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