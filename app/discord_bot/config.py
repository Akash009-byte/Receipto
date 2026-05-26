import os
import logging

logger = logging.getLogger(__name__)

# Discord Bot Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DUMP_CHANNEL_ID = os.getenv("DUMP_CHANNEL_ID")

def validate_config():
    """Check if required Discord configuration is present."""
    logger.info(f"Validating Discord config - Token: {'SET' if DISCORD_BOT_TOKEN else 'NOT SET'}, Channel: {'SET' if DUMP_CHANNEL_ID else 'NOT SET'}")
    
    if not DISCORD_BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN environment variable is required")
        raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
    
    if not DUMP_CHANNEL_ID:
        logger.error("DUMP_CHANNEL_ID environment variable is required")
        raise ValueError("DUMP_CHANNEL_ID environment variable is required")
    
    logger.info("Discord configuration validated successfully")
    return True 