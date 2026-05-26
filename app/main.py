from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
import uvicorn
from api.router_config import api_router
from core import postgres
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import psutil
import logging
from discord_bot.service import DiscordService
from api.routes.discord_routes import set_discord_service

SERVER_PORT = int(os.getenv("SERVER_PORT", 5001))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Discord service instance
discord_service_instance = None


def is_primary_worker() -> bool:
    """
    Determine if this process is the primary (lowest PID) Gunicorn worker.
    Works regardless of worker class and without relying on post_fork.
    """
    try:
        current_pid = os.getpid()
        parent = psutil.Process().parent()
        child_pids = [p.pid for p in parent.children()]
        return current_pid == min(child_pids)
    except Exception as e:
        logger.warning(f"Could not determine primary worker: {e}")
        return True  # Default to True in non-Gunicorn runs


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application.")
    await postgres.connect_postgresql()

    global discord_service_instance
    if is_primary_worker():
        try:
            # Start Discord bot
            logger.info("Primary worker detected — starting Discord service...")
            discord_service_instance = DiscordService()
            await discord_service_instance.start()

            # Make bot instance available to routes
            set_discord_service(discord_service_instance)

            logger.info("Discord service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Discord service: {e}")
    else:
        logger.info("Secondary worker detected — skipping Discord service startup.")

    yield

    # Stop Discord service only if running in primary worker
    if is_primary_worker() and discord_service_instance:
        logger.info("Primary worker shutting down Discord service...")
        await discord_service_instance.stop()

    await postgres.disconnect_postgresql()
    logger.info("Stopping FastAPI application.")


app = FastAPI(lifespan=lifespan)

origins = [
    "*",  # This configuration is intended for development purpose, it's **your** responsibility to harden it for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=SERVER_PORT, reload=True)
