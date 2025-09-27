"""
Aimbot detection algorithms

This module contains functions for detecting aimbot usage based on player statistics
and behavioral patterns.
"""

from typing import Dict, Any


def calculate_aimbot_score(player_data: Dict[str, Any]) -> float:
    """
    Calculate aimbot suspicion score based on player statistics.

    Args:
        player_data: Dictionary containing player statistics
                   - headshot_percentage: float (0-100)
                   - reaction_time_avg: float (seconds)
                   - crosshair_placement_score: float (0-100)
                   - flick_shot_accuracy: float (0-100)

    Returns:
        float: Suspicion score (0-100), higher = more suspicious
    """
    score = 0.0

    # High headshot percentage is suspicious
    headshot_pct = player_data.get("headshot_percentage", 0.0)
    if headshot_pct > 80:
        score += 30
    elif headshot_pct > 60:
        score += 15
    elif headshot_pct > 40:
        score += 5

    # Very fast reaction times are suspicious
    reaction_time = player_data.get("reaction_time_avg", 0.3)
    if reaction_time < 0.1:  # 100ms
        score += 25
    elif reaction_time < 0.15:  # 150ms
        score += 15
    elif reaction_time < 0.2:  # 200ms
        score += 5

    # Perfect crosshair placement is suspicious
    crosshair_score = player_data.get("crosshair_placement_score", 0.0)
    if crosshair_score > 95:
        score += 20
    elif crosshair_score > 85:
        score += 10
    elif crosshair_score > 75:
        score += 3

    # Perfect flick shots are highly suspicious
    flick_accuracy = player_data.get("flick_shot_accuracy", 0.0)
    if flick_accuracy > 90:
        score += 25
    elif flick_accuracy > 70:
        score += 10
    elif flick_accuracy > 50:
        score += 3

    # Cap at 100
    return min(score, 100.0)