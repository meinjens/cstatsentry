from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, DECIMAL, JSON, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Player(Base):
    __tablename__ = "players"

    steam_id = Column(String(17), primary_key=True)
    current_name = Column(String(255))
    previous_names = Column(JSON)  # Store as JSON array for SQLite compatibility
    avatar_url = Column(String)
    profile_url = Column(String)

    # Profile data
    account_created = Column(DateTime)
    last_logoff = Column(DateTime)
    profile_state = Column(Integer)  # 0=not configured, 1=configured
    visibility_state = Column(Integer)  # 1=private, 3=public
    country_code = Column(String(3))

    # Playtime data
    cs2_hours = Column(Integer, default=0)
    total_games_owned = Column(Integer, default=0)

    # Cache timestamps
    profile_updated = Column(DateTime)
    stats_updated = Column(DateTime)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    bans = relationship("PlayerBan", back_populates="player", uselist=False)
    analyses = relationship("PlayerAnalysis", back_populates="player")
    match_players = relationship("MatchPlayer", back_populates="player")
    user_teammates = relationship("UserTeammate", back_populates="player")


class PlayerBan(Base):
    __tablename__ = "player_bans"

    steam_id = Column(String(17), ForeignKey("players.steam_id"), primary_key=True)
    community_banned = Column(Boolean, default=False)
    vac_banned = Column(Boolean, default=False)
    number_of_vac_bans = Column(Integer, default=0)
    days_since_last_ban = Column(Integer, default=0)
    number_of_game_bans = Column(Integer, default=0)
    economy_ban = Column(String(20), default='none')  # none, probation, banned
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    player = relationship("Player", back_populates="bans")


class PlayerAnalysis(Base):
    __tablename__ = "player_analyses"

    analysis_id = Column(Integer, primary_key=True, index=True)
    steam_id = Column(String(17), ForeignKey("players.steam_id"), nullable=False)
    analyzed_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    suspicion_score = Column(Integer)  # 0-100
    flags = Column(JSON)  # Flexible storage for different flag types
    confidence_level = Column(DECIMAL(3, 2))  # 0.00 - 1.00
    analysis_version = Column(String(10))  # For algorithm versioning
    notes = Column(String)
    analyzed_at = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    player = relationship("Player", back_populates="analyses")
    analyzer = relationship("User", foreign_keys=[analyzed_by], back_populates="analyses")