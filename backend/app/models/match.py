from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, DECIMAL
from sqlalchemy.orm import relationship
from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"

    match_id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    match_date = Column(DateTime, nullable=False)
    map = Column(String(100))
    score_team1 = Column(Integer)
    score_team2 = Column(Integer)
    user_team = Column(Integer)  # 1 or 2
    sharing_code = Column(String(255))
    leetify_match_id = Column(String(255))
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="matches")
    match_players = relationship("MatchPlayer", back_populates="match")


class MatchPlayer(Base):
    __tablename__ = "match_players"

    match_id = Column(String(255), ForeignKey("matches.match_id"), primary_key=True)
    steam_id = Column(String(17), ForeignKey("players.steam_id"), primary_key=True)
    team = Column(Integer)  # 1 or 2
    score = Column(Integer, default=0)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    headshot_percentage = Column(DECIMAL(5, 2))

    # Relationships
    match = relationship("Match", back_populates="match_players")
    player = relationship("Player", back_populates="match_players")