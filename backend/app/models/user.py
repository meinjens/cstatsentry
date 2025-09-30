from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    steam_id = Column(String(17), unique=True, nullable=False, index=True)
    steam_name = Column(String(255))
    avatar_url = Column(String)
    last_sync = Column(DateTime)
    sync_enabled = Column(Boolean, default=True)

    # Steam Match Sharing Codes for accessing match history
    steam_auth_code = Column(String(255))  # Authentication code from CS2
    last_match_sharecode = Column(String(50))  # Last processed match sharecode (CSGO-xxxxx-xxxxx-...)

    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    matches = relationship("Match", back_populates="user")
    analyses = relationship("PlayerAnalysis", foreign_keys="[PlayerAnalysis.analyzed_by]", back_populates="analyzer")
    teammates = relationship("UserTeammate", back_populates="user")