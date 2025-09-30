"""
CS2/CSGO Demo File Downloader

Downloads demo files (.dem.bz2) from Valve's replay servers.
Demo files contain complete match data that can be parsed for detailed analysis.
"""

import aiohttp
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DemoDownloader:
    """Service for downloading CS2/CSGO demo files"""

    def __init__(self, download_dir: str = "/tmp/cstatsentry/demos"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_demo_filename(self, match_id: int, outcome_id: int) -> str:
        """Get the demo filename for a match"""
        return f"{str(match_id).zfill(21)}_{str(outcome_id).zfill(10)}.dem.bz2"

    def get_local_path(self, match_id: int, outcome_id: int) -> Path:
        """Get local filesystem path for demo file"""
        filename = self.get_demo_filename(match_id, outcome_id)
        return self.download_dir / filename

    async def download_demo(
        self,
        demo_url: str,
        match_id: int,
        outcome_id: int,
        force: bool = False
    ) -> Optional[Path]:
        """
        Download a demo file from Valve's replay servers

        Args:
            demo_url: Full URL to the demo file
            match_id: Match ID
            outcome_id: Outcome ID
            force: Force re-download even if file exists

        Returns:
            Path to downloaded file or None if download failed
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use 'async with' context manager.")

        local_path = self.get_local_path(match_id, outcome_id)

        # Check if already downloaded
        if local_path.exists() and not force:
            logger.info(f"Demo already exists: {local_path}")
            return local_path

        try:
            logger.info(f"Downloading demo from {demo_url}")

            async with self.session.get(demo_url, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status != 200:
                    logger.error(f"Failed to download demo: HTTP {response.status}")
                    return None

                # Get file size for progress tracking
                total_size = int(response.headers.get('content-length', 0))
                logger.info(f"Demo file size: {total_size / 1024 / 1024:.2f} MB")

                # Download in chunks
                downloaded = 0
                chunk_size = 1024 * 1024  # 1MB chunks

                with open(local_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (chunk_size * 5) == 0:  # Log every 5MB
                                logger.debug(f"Download progress: {progress:.1f}%")

                logger.info(f"Demo downloaded successfully: {local_path}")
                return local_path

        except asyncio.TimeoutError:
            logger.error(f"Demo download timed out: {demo_url}")
            return None
        except Exception as e:
            logger.error(f"Error downloading demo: {e}")
            return None

    async def download_match_demos(
        self,
        matches: list,
        max_concurrent: int = 3
    ) -> list:
        """
        Download demo files for multiple matches concurrently

        Args:
            matches: List of match dictionaries with demo_url, match_id, outcome_id
            max_concurrent: Maximum number of concurrent downloads

        Returns:
            List of tuples (match_data, local_path) for successfully downloaded demos
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_semaphore(match_data):
            async with semaphore:
                path = await self.download_demo(
                    match_data["demo_url"],
                    match_data["match_id"],
                    match_data["outcome_id"]
                )
                return (match_data, path)

        tasks = [download_with_semaphore(match) for match in matches]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failures and exceptions
        successful = [
            (match, path) for match, path in results
            if not isinstance((match, path), Exception) and path is not None
        ]

        logger.info(f"Successfully downloaded {len(successful)}/{len(matches)} demos")
        return successful

    def cleanup_old_demos(self, keep_recent: int = 100):
        """
        Clean up old demo files, keeping only the most recent ones

        Args:
            keep_recent: Number of recent demos to keep
        """
        demo_files = sorted(
            self.download_dir.glob("*.dem.bz2"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if len(demo_files) <= keep_recent:
            return

        removed_count = 0
        for demo_file in demo_files[keep_recent:]:
            try:
                demo_file.unlink()
                removed_count += 1
            except Exception as e:
                logger.error(f"Failed to delete {demo_file}: {e}")

        logger.info(f"Cleaned up {removed_count} old demo files")

    def get_demo_info(self, match_id: int, outcome_id: int) -> Optional[dict]:
        """Get information about a downloaded demo file"""
        local_path = self.get_local_path(match_id, outcome_id)

        if not local_path.exists():
            return None

        stat = local_path.stat()
        return {
            "path": str(local_path),
            "size": stat.st_size,
            "size_mb": stat.st_size / 1024 / 1024,
            "downloaded_at": stat.st_mtime,
            "exists": True
        }


async def get_demo_downloader() -> DemoDownloader:
    """Factory function to create demo downloader"""
    return DemoDownloader()


# Example usage
if __name__ == "__main__":
    from app.services.steam_sharecode import decode_sharecode, get_demo_url

    async def test_download():
        test_sharecode = "CSGO-U6MWi-5cZMJ-VsXtM-yrOwD-g8BJJ"

        decoded = decode_sharecode(test_sharecode)
        if not decoded:
            print("Failed to decode sharecode")
            return

        demo_url = get_demo_url(
            decoded["matchId"],
            decoded["outcomeId"],
            decoded["tokenId"]
        )

        print(f"Demo URL: {demo_url}")

        async with DemoDownloader() as downloader:
            path = await downloader.download_demo(
                demo_url,
                decoded["matchId"],
                decoded["outcomeId"]
            )

            if path:
                print(f"Downloaded to: {path}")
                info = downloader.get_demo_info(decoded["matchId"], decoded["outcomeId"])
                print(f"File info: {info}")
            else:
                print("Download failed")

    asyncio.run(test_download())