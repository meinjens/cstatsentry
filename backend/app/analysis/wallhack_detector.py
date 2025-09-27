"""
Wallhack detection algorithms

This module contains functions for detecting wallhack usage based on player behavior
and positioning patterns.
"""

from typing import Dict, Any


def calculate_wallhack_score(player_data: Dict[str, Any]) -> float:
    """
    Calculate wallhack suspicion score based on player behavior.

    Args:
        player_data: Dictionary containing player behavior statistics
                   - pre_fire_percentage: float (0-100)
                   - wall_bang_accuracy: float (0-100)
                   - enemy_tracking_through_walls: float (0-100)
                   - suspicious_positioning: float (0-100)

    Returns:
        float: Suspicion score (0-100), higher = more suspicious
    """
    score = 0.0

    # High pre-fire percentage indicates pre-knowledge
    pre_fire_pct = player_data.get("pre_fire_percentage", 0.0)
    if pre_fire_pct > 60:
        score += 30
    elif pre_fire_pct > 40:
        score += 20
    elif pre_fire_pct > 20:
        score += 10

    # High wall bang accuracy is suspicious
    wall_bang_accuracy = player_data.get("wall_bang_accuracy", 0.0)
    if wall_bang_accuracy > 80:
        score += 25
    elif wall_bang_accuracy > 60:
        score += 15
    elif wall_bang_accuracy > 40:
        score += 8

    # Tracking enemies through walls
    tracking_score = player_data.get("enemy_tracking_through_walls", 0.0)
    if tracking_score > 70:
        score += 20
    elif tracking_score > 50:
        score += 12
    elif tracking_score > 30:
        score += 5

    # Suspicious positioning (always in optimal spots)
    positioning_score = player_data.get("suspicious_positioning", 0.0)
    if positioning_score > 80:
        score += 15
    elif positioning_score > 60:
        score += 10
    elif positioning_score > 40:
        score += 5

    # Cap at 100
    return min(score, 100.0)