import os
import asyncio
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.log_config import logger
from alembic.config import Config
from alembic import command

POSTGRESQL_DB_URL = os.getenv("POSTGRESQL_DB_URL")

# Create an async SQLAlchemy engine
async_engine = create_async_engine(POSTGRESQL_DB_URL, echo=True)

# Create an async session maker
AsyncSessionLocal = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

async def run_migrations():
    """Load alembic.ini and run migrations programmatically."""
    alembic_cfg = Config("./alembic.ini")
    # Run synchronous Alembic command in a separate thread
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")

# Dependency to get the session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def connect_postgresql():
    async with async_engine.begin() as connection:
        await connection.execute(text("SELECT 1"))
        logger.info("PostgreSQL connected successfully!")

async def disconnect_postgresql():
    await async_engine.dispose()  # This will close all connections in the pool
    logger.info("PostgreSQL connection pool closed.")
