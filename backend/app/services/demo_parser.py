"""
CS2/CSGO Demo Parser Integration

Parses .dem demo files to extract detailed match information.

Note: This is a basic integration placeholder. For production use, consider:
- demoparser2: https://github.com/LaihoE/demoparser2 (Rust-based, very fast)
- awpy: https://github.com/pnxenopoulos/awpy (Python-based, comprehensive)

Demo files are compressed with bzip2 and contain:
- Player movements and positions
- Kills, deaths, assists
- Round outcomes
- Equipment purchases
- Damage events
- etc.
"""

import bz2
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DemoParser:
    """Basic demo parser - placeholder for full implementation"""

    def __init__(self):
        self.parser_available = False
        self._check_parser_availability()

    def _check_parser_availability(self):
        """Check if a demo parsing library is available"""
        try:
            # Try importing demoparser2
            import demoparser2
            self.parser_available = True
            self.parser_type = "demoparser2"
            logger.info("Using demoparser2 for demo parsing")
        except ImportError:
            try:
                # Try importing awpy
                import awpy
                self.parser_available = True
                self.parser_type = "awpy"
                logger.info("Using awpy for demo parsing")
            except ImportError:
                logger.warning("No demo parser library available. Install demoparser2 or awpy.")
                self.parser_available = False
                self.parser_type = None

    def decompress_demo(self, demo_path: Path) -> Optional[Path]:
        """
        Decompress a .dem.bz2 file to .dem

        Args:
            demo_path: Path to compressed demo file

        Returns:
            Path to decompressed demo or None if failed
        """
        try:
            if not demo_path.exists():
                logger.error(f"Demo file not found: {demo_path}")
                return None

            # Output path without .bz2 extension
            output_path = demo_path.with_suffix('')

            if output_path.exists():
                logger.info(f"Decompressed demo already exists: {output_path}")
                return output_path

            logger.info(f"Decompressing {demo_path}")

            with bz2.open(demo_path, 'rb') as compressed:
                with open(output_path, 'wb') as decompressed:
                    decompressed.write(compressed.read())

            logger.info(f"Decompressed to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to decompress demo: {e}")
            return None

    def parse_demo_basic(self, demo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse demo file to extract basic match information

        Args:
            demo_path: Path to demo file (.dem or .dem.bz2)

        Returns:
            Dictionary with match data or None if parsing failed
        """
        try:
            # Decompress if needed
            if demo_path.suffix == '.bz2':
                demo_path = self.decompress_demo(demo_path)
                if not demo_path:
                    return None

            if not self.parser_available:
                logger.error("No demo parser available")
                return self._extract_basic_metadata(demo_path)

            # Use available parser
            if self.parser_type == "demoparser2":
                return self._parse_with_demoparser2(demo_path)
            elif self.parser_type == "awpy":
                return self._parse_with_awpy(demo_path)

            return None

        except Exception as e:
            logger.error(f"Failed to parse demo: {e}")
            return None

    def _extract_basic_metadata(self, demo_path: Path) -> Dict[str, Any]:
        """
        Extract basic metadata without full parsing
        This is a fallback when no parser library is available
        """
        return {
            "parsed": False,
            "parser": "basic_metadata",
            "file_path": str(demo_path),
            "file_size": demo_path.stat().st_size,
            "message": "No demo parser library available. Install demoparser2 or awpy for full parsing."
        }

    def _parse_with_demoparser2(self, demo_path: Path) -> Dict[str, Any]:
        """Parse demo using demoparser2 library"""
        try:
            import demoparser2

            # Parse demo
            parser = demoparser2.DemoParser(str(demo_path))

            # Extract match data
            header = parser.parse_header()
            events = parser.parse_events(["player_death", "round_end"])

            # Process players
            players = []
            player_stats = {}

            # Process kills
            for event in events.get("player_death", []):
                attacker_id = event.get("attacker_steamid")
                victim_id = event.get("victim_steamid")

                if attacker_id not in player_stats:
                    player_stats[attacker_id] = {"kills": 0, "deaths": 0, "headshots": 0}
                if victim_id not in player_stats:
                    player_stats[victim_id] = {"kills": 0, "deaths": 0, "headshots": 0}

                player_stats[attacker_id]["kills"] += 1
                player_stats[victim_id]["deaths"] += 1

                if event.get("headshot"):
                    player_stats[attacker_id]["headshots"] += 1

            # Convert to list format
            players = [
                {
                    "steam_id": steam_id,
                    **stats
                }
                for steam_id, stats in player_stats.items()
            ]

            return {
                "parsed": True,
                "parser": "demoparser2",
                "map": header.get("map_name"),
                "duration": header.get("duration"),
                "players": players,
                "rounds": len(events.get("round_end", [])),
                "kills": len(events.get("player_death", []))
            }

        except Exception as e:
            logger.error(f"demoparser2 parsing failed: {e}")
            return None

    def _parse_with_awpy(self, demo_path: Path) -> Dict[str, Any]:
        """Parse demo using awpy library"""
        try:
            from awpy import Demo

            # Parse demo
            demo = Demo(str(demo_path))
            data = demo.parse()

            # Extract player stats
            players = []
            if "players" in data:
                for player_data in data["players"]:
                    players.append({
                        "steam_id": player_data.get("steamid"),
                        "player_name": player_data.get("name"),
                        "kills": player_data.get("kills", 0),
                        "deaths": player_data.get("deaths", 0),
                        "assists": player_data.get("assists", 0),
                        "team": player_data.get("team")
                    })

            return {
                "parsed": True,
                "parser": "awpy",
                "map": data.get("map"),
                "players": players,
                "rounds": len(data.get("rounds", [])),
                "score_team1": data.get("score", {}).get("team1", 0),
                "score_team2": data.get("score", {}).get("team2", 0)
            }

        except Exception as e:
            logger.error(f"awpy parsing failed: {e}")
            return None


# Integration function for match sync
async def parse_demo_for_match(demo_path: Path) -> Optional[Dict[str, Any]]:
    """
    Async wrapper for demo parsing to use in match sync tasks

    Args:
        demo_path: Path to demo file

    Returns:
        Parsed match data or None
    """
    parser = DemoParser()
    return parser.parse_demo_basic(demo_path)


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    def test_parser():
        parser = DemoParser()
        print(f"Parser available: {parser.parser_available}")
        print(f"Parser type: {parser.parser_type}")

        # Test with a demo file if available
        test_demo = Path("/tmp/cstatsentry/demos/test.dem.bz2")
        if test_demo.exists():
            result = parser.parse_demo_basic(test_demo)
            print(f"Parse result: {result}")
        else:
            print(f"No test demo found at {test_demo}")

    test_parser()