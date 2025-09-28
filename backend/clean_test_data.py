#!/usr/bin/env python3
"""
Clean test data and run fresh match sync test
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.match import Match, MatchPlayer
from app.models.player import Player


def clean_test_data():
    """Clean all test data"""
    db = SessionLocal()
    try:
        print("🧹 Cleaning test data...")

        # Delete match players first (foreign key constraint)
        match_players_deleted = db.query(MatchPlayer).delete()
        print(f"   Deleted {match_players_deleted} match players")

        # Delete matches
        matches_deleted = db.query(Match).delete()
        print(f"   Deleted {matches_deleted} matches")

        # Delete players
        players_deleted = db.query(Player).delete()
        print(f"   Deleted {players_deleted} players")

        db.commit()
        print("✅ Test data cleaned successfully")

    except Exception as e:
        print(f"❌ Error cleaning data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    clean_test_data()