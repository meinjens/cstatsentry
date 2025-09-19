from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserTeammate(Base):
    __tablename__ = "user_teammates"

    relation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    player_steam_id = Column(String(17), ForeignKey("players.steam_id"), nullable=False)
    matches_together = Column(Integer, default=1)
    first_seen = Column(DateTime, server_default=func.current_timestamp())
    last_seen = Column(DateTime, server_default=func.current_timestamp())
    relationship_type = Column(String(20), default='teammate')  # teammate, opponent

    __table_args__ = (UniqueConstraint('user_id', 'player_steam_id', name='_user_player_uc'),)

    # Relationships
    user = relationship("User", back_populates="teammates")
    player = relationship("Player", back_populates="user_teammates")