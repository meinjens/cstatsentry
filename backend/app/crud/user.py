from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_steam_id(db: Session, steam_id: str) -> Optional[User]:
    """Get user by Steam ID"""
    return db.query(User).filter(User.steam_id == steam_id).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by user ID"""
    return db.query(User).filter(User.user_id == user_id).first()


def create_user(db: Session, user_data: dict) -> User:
    """Create a new user"""
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, update_data: dict) -> User:
    """Update an existing user"""
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user