from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from discord_bot.service import DiscordService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/discord')

# Global Discord service instance
_discord_service = None

def set_discord_service(service: DiscordService):
    """Set the global Discord service instance."""
    global _discord_service
    _discord_service = service

def get_discord_service() -> DiscordService:
    """Get the global Discord service instance."""
    return _discord_service

class MessageRequest(BaseModel):
    message: str

@router.post("/send")
async def send_message(request: MessageRequest):
    """Send a message to Discord #dump channel."""
    discord_service = get_discord_service()
    
    if not discord_service or not discord_service.is_connected():
        raise HTTPException(status_code=503, detail="Discord service not connected")
    
    try:
        success = await discord_service.send_message(request.message)
        if success:
            return {"status": "success", "message": "Message sent to Discord"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")
    except Exception as e:
        logger.error(f"Error sending Discord message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/status")
async def get_status():
    """Get Discord service status."""
    discord_service = get_discord_service()
    
    if not discord_service:
        return {"status": "not_initialized"}
    
    return {
        "status": "connected" if discord_service.is_connected() else "disconnected"
    } 