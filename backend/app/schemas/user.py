from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    steam_id: str
    steam_name: Optional[str] = None
    avatar_url: Optional[str] = None
    sync_enabled: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    steam_name: Optional[str] = None
    avatar_url: Optional[str] = None
    sync_enabled: Optional[bool] = None


class User(UserBase):
    user_id: int
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True