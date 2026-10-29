import aiohttp
import os
import logging
from typing import Optional
from datetime import datetime
import urllib.parse

logger = logging.getLogger(__name__)

class ImageDownloader:
    """Utility class for downloading images from Discord URLs."""

    def __init__(self, download_folder: str = "dump"):
        self.download_folder = download_folder
        self.ensure_download_folder_exists()

    def ensure_download_folder_exists(self):
        """Create the download folder if it doesn't exist."""
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            logger.info(f"📁 Created download folder: {self.download_folder}")

    def generate_filename(self, original_filename: str, user_name: str) -> str:
        """Generate a unique filename for the downloaded image."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Clean the username (remove special characters)
        clean_username = "".join(c for c in user_name if c.isalnum() or c in ('-', '_'))

        # Get file extension
        _, ext = os.path.splitext(original_filename)
        if not ext:
            ext = '.jpg'  # Default extension

        # Create unique filename
        filename = f"{timestamp}_{clean_username}_{original_filename}"

        # Ensure filename is not too long
        if len(filename) > 200:
            base_name = f"{timestamp}_{clean_username}_receipt"
            filename = base_name + ext

        return filename

    async def download_image(self, url: str, filename: str) -> Optional[str]:
        """Download image from URL and save to local file."""
        try:
            logger.info(f"📥 Downloading image from: {url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        file_path = os.path.join(self.download_folder, filename)

                        with open(file_path, 'wb') as file:
                            async for chunk in response.content.iter_chunked(8192):
                                file.write(chunk)

                        file_size = os.path.getsize(file_path)
                        logger.info(f"✅ Image downloaded successfully: {file_path} ({file_size} bytes)")
                        return file_path
                    else:
                        logger.error(f"❌ Failed to download image: HTTP {response.status}")
                        return None

        except Exception as e:
            logger.error(f"❌ Error downloading image: {e}")
            return None

    async def download_discord_attachment(self, attachment, user_name: str) -> Optional[str]:
        """Download a Discord attachment and return the local file path."""
        try:
            # Generate unique filename
            filename = self.generate_filename(attachment.filename, user_name)

            # Download the image
            file_path = await self.download_image(attachment.url, filename)

            if file_path:
                logger.info(f"📸 Successfully downloaded attachment: {filename}")
                return file_path
            else:
                logger.error(f"❌ Failed to download attachment: {attachment.filename}")
                return None

        except Exception as e:
            logger.error(f"❌ Error processing Discord attachment: {e}")
            return None

    def get_downloaded_files_count(self) -> int:
        """Get the number of files in the download folder."""
        try:
            return len([f for f in os.listdir(self.download_folder)
                       if os.path.isfile(os.path.join(self.download_folder, f))])
        except Exception:
            return 0

    def cleanup_old_files(self, max_files: int = 100):
        """Remove old files if folder has too many files."""
        try:
            files = []
            for f in os.listdir(self.download_folder):
                file_path = os.path.join(self.download_folder, f)
                if os.path.isfile(file_path):
                    files.append((file_path, os.path.getctime(file_path)))

            if len(files) > max_files:
                # Sort by creation time (oldest first)
                files.sort(key=lambda x: x[1])

                # Remove oldest files
                files_to_remove = len(files) - max_files
                for i in range(files_to_remove):
                    os.remove(files[i][0])
                    logger.info(f"🗑️ Removed old file: {files[i][0]}")

        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
