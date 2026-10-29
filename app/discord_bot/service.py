import asyncio
import logging
from .bot import DiscordBot

logger = logging.getLogger(__name__)

class DiscordService:
    def __init__(self):
        self.bot = DiscordBot()
        self._bot_task = None

    async def start(self):
        """Start the Discord service."""
        try:
            # Start bot in background
            self._bot_task = asyncio.create_task(self.bot.start_bot())
            logger.info("Discord service started")

            # Wait a bit for connection
            # It is taking minimum 5 seconds to connect to Discord
            await asyncio.sleep(5)

            if not self.bot.is_connected:
                logger.warning("Discord bot not connected after 2 seconds")
        except Exception as e:
            logger.error(f"Failed to start Discord service: {e}")
            raise

    async def stop(self):
        """Stop the Discord service."""
        try:
            if self._bot_task:
                self._bot_task.cancel()
                try:
                    await self._bot_task
                except asyncio.CancelledError:
                    pass

            await self.bot.stop_bot()
            logger.info("Discord service stopped")
        except Exception as e:
            logger.error(f"Error stopping Discord service: {e}")

    async def send_message(self, message: str):
        """Send a message to Discord."""
        return await self.bot.send_message(message)

    def is_connected(self):
        """Check if bot is connected."""
        return self.bot.is_connected
