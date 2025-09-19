from celery import current_task
from app.core.celery import celery_app
from app.db.session import SessionLocal
from app.crud.player import (
    get_player_by_steam_id,
    update_player,
    create_or_update_player_ban,
    create_player_analysis
)
from app.services.steam_api import steam_api, SteamDataExtractor
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def analyze_player_profile(self, steam_id: str, force_update: bool = False, analyzed_by: int = None):
    """Deep analysis of player profile and statistics"""
    db = SessionLocal()
    try:
        player = get_player_by_steam_id(db, steam_id)
        if not player:
            logger.error(f"Player {steam_id} not found")
            return {"status": "error", "message": "Player not found"}

        logger.info(f"Analyzing player {steam_id}")

        # Check if we need to update profile data
        needs_update = force_update or not player.profile_updated or \
                      (datetime.utcnow() - player.profile_updated) > timedelta(days=1)

        if needs_update:
            # Fetch fresh data from Steam API
            async with steam_api:
                # Get player summary
                summary_data = await steam_api.get_player_summaries([steam_id])
                if summary_data.get("response", {}).get("players"):
                    player_info = summary_data["response"]["players"][0]
                    extracted_data = SteamDataExtractor.extract_player_data(player_info)

                    # Update player profile
                    update_data = {**extracted_data, "profile_updated": datetime.utcnow()}
                    update_player(db, player, update_data)

                # Get ban information
                ban_data = await steam_api.get_player_bans([steam_id])
                if ban_data.get("players"):
                    ban_info = ban_data["players"][0]
                    extracted_ban_data = SteamDataExtractor.extract_ban_data(ban_info)
                    create_or_update_player_ban(db, extracted_ban_data)

                # Get owned games for playtime analysis
                try:
                    games_data = await steam_api.get_owned_games(steam_id)
                    cs2_hours = SteamDataExtractor.extract_cs2_hours(games_data)
                    total_games = SteamDataExtractor.extract_total_games(games_data)

                    update_player(db, player, {
                        "cs2_hours": cs2_hours,
                        "total_games_owned": total_games,
                        "stats_updated": datetime.utcnow()
                    })
                except Exception as e:
                    logger.warning(f"Could not fetch games for {steam_id}: {e}")

        # Calculate suspicion score
        suspicion_data = calculate_suspicion_score(player)

        # Create analysis record
        if analyzed_by:
            analysis_data = {
                "steam_id": steam_id,
                "analyzed_by": analyzed_by,
                "suspicion_score": suspicion_data["score"],
                "flags": suspicion_data["flags"],
                "confidence_level": suspicion_data["confidence"],
                "analysis_version": "1.0",
                "notes": suspicion_data.get("notes")
            }
            create_player_analysis(db, analysis_data)

        return {
            "status": "completed",
            "steam_id": steam_id,
            "suspicion_score": suspicion_data["score"],
            "flags": suspicion_data["flags"]
        }

    except Exception as e:
        logger.error(f"Error analyzing player {steam_id}: {e}")
        self.retry(countdown=60, max_retries=2)
    finally:
        db.close()


def calculate_suspicion_score(player) -> dict:
    """
    Calculate suspicion score based on player data
    Score Range: 0-100
    """
    score = 0
    flags = {}
    confidence = 0.8

    # Profile flags (max 40 points)
    profile_score, profile_flags = calculate_profile_flags(player)
    score += profile_score
    flags.update(profile_flags)

    # Statistical anomalies (max 40 points)
    stats_score, stats_flags = calculate_statistical_flags(player)
    score += stats_score
    flags.update(stats_flags)

    # Historical patterns (max 20 points)
    history_score, history_flags = calculate_historical_flags(player)
    score += history_score
    flags.update(history_flags)

    return {
        "score": min(score, 100),
        "flags": flags,
        "confidence": confidence,
        "notes": f"Analysis based on {len(flags)} detection criteria"
    }


def calculate_profile_flags(player) -> tuple[int, dict]:
    """Calculate profile-based flags"""
    score = 0
    flags = {}

    # New account flag (10 points)
    if player.account_created:
        account_age_days = (datetime.utcnow() - datetime.fromtimestamp(player.account_created)).days
        if account_age_days < 30:
            score += 10
            flags["new_account"] = {
                "severity": "medium",
                "description": f"Account created {account_age_days} days ago",
                "value": account_age_days
            }

    # Private profile flag (15 points)
    if player.visibility_state == 1:  # Private profile
        score += 15
        flags["private_profile"] = {
            "severity": "high",
            "description": "Profile is private",
            "value": True
        }

    # Limited games flag (10 points)
    if player.total_games_owned < 5:
        score += 10
        flags["limited_games"] = {
            "severity": "medium",
            "description": f"Only {player.total_games_owned} games owned",
            "value": player.total_games_owned
        }

    # CS2 only player flag (5 points)
    if player.total_games_owned <= 3 and player.cs2_hours > 100:
        score += 5
        flags["cs2_only"] = {
            "severity": "low",
            "description": "Primarily plays CS2 with few other games",
            "value": True
        }

    return score, flags


def calculate_statistical_flags(player) -> tuple[int, dict]:
    """Calculate statistics-based flags"""
    score = 0
    flags = {}

    # TODO: Implement when we have match statistics
    # - Performance spikes
    # - Headshot rate analysis
    # - Consistency patterns
    # - Skill vs hours correlation

    return score, flags


def calculate_historical_flags(player) -> tuple[int, dict]:
    """Calculate historical pattern flags"""
    score = 0
    flags = {}

    # TODO: Implement when we have historical data
    # - Name change frequency
    # - Country changes
    # - Performance trends over time

    return score, flags


@celery_app.task(bind=True)
def batch_analyze_players(self, steam_ids: list[str], analyzed_by: int = None):
    """Analyze multiple players in batch"""
    results = []

    for steam_id in steam_ids:
        try:
            result = analyze_player_profile.delay(steam_id, analyzed_by=analyzed_by)
            results.append({"steam_id": steam_id, "task_id": result.id})
        except Exception as e:
            logger.error(f"Failed to queue analysis for {steam_id}: {e}")
            results.append({"steam_id": steam_id, "error": str(e)})

    return {
        "status": "queued",
        "total_players": len(steam_ids),
        "results": results
    }