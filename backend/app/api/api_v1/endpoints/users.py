from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import User as UserSchema, UserUpdate
from app.crud.user import update_user
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    update_data = user_update.dict(exclude_unset=True)
    updated_user = update_user(db, current_user, update_data)
    return updated_user