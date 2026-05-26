import discord
import asyncio
import logging
from .config import DISCORD_BOT_TOKEN, DUMP_CHANNEL_ID, validate_config
from .message_events import MessageEvents

logger = logging.getLogger(__name__)

class DiscordBot:
    def __init__(self):
        self.bot = None
        self.is_connected = False
        self.message_events = None
    
    async def start_bot(self):
        """Start the Discord bot."""
        try:
            # Validate configuration
            validate_config()
            logger.info("Starting Discord bot...")
            
            # Create bot with intents
            intents = discord.Intents.default()
            intents.message_content = True
            
            self.bot = discord.Client(intents=intents)
            
            # Initialize message events handler
            self.message_events = MessageEvents(self.bot)
            
            @self.bot.event
            async def on_ready():
                logger.info(f'Bot connected as {self.bot.user}')
                self.is_connected = True
                
                # Set bot status
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching,
                        name="receipto"
                    )
                )
            
            @self.bot.event
            async def on_disconnect():
                logger.warning("Bot disconnected from Discord")
                self.is_connected = False
            
            @self.bot.event
            async def on_error(event, *args, **kwargs):
                logger.error(f"Discord error in event {event}: {args} {kwargs}")
            
            logger.info("Attempting to connect to Discord...")
            # Start the bot
            await self.bot.start(DISCORD_BOT_TOKEN)
            
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the Discord bot."""
        if self.bot:
            await self.bot.close()
            self.is_connected = False
            logger.info("Discord bot stopped")
    
    async def send_message(self, message: str):
        """Send a message to the #dump channel."""
        if not self.bot or not self.is_connected:
            logger.error("Bot not connected")
            return False
        
        try:
            channel = self.bot.get_channel(int(DUMP_CHANNEL_ID))
            if channel:
                await channel.send(message)
                logger.info(f"Message sent to #dump: {message[:50]}...")
                return True
            else:
                logger.error(f"Channel {DUMP_CHANNEL_ID} not found")
                return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False 