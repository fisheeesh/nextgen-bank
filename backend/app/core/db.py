import asyncio
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

"""
Connection pooling is basically the practice of managing a pool of database connections to reuse them
instead of creating new ones. This baiscally help use to improve the perfornace by reducing 
the overhead of establishing and tearing down connections for each request.
"""

# ? An engine is basically the starting poirt for any SQLalchemy application
# ? It's going to hold the connection pool and the connection to the database
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    # ? to create a connection pool -> this pool is gonna to maintain a queue of connections to the database that can be reused
    # $ That's a benefit to use cuz we're gonna be reusing connections instead of creating new ones and thus reducing the database connection overhead
    poolclass=AsyncAdaptedQueuePool,
    # ? enables that health checks before providing a connection from the pool
    # ? This is gonna help us to detect stale connections before they used
    pool_pre_ping=True,
    # ? max number of permanent connections to keep in the pool -> maintina up to 5 connections to the databae at any time
    pool_size=5,
    # ? max number of additional connections that can be created beyond the pool size
    max_overflow=10,
    # ? number of seconds to wait for a connection from the pool before giving up
    pool_timeout=30,
    # ? number of seconds after which a connection is recycled -> helps us prevent stale connections from being used
    pool_recycle=1800,
)


# ? a factory method for databse sessions
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        if session:
            try:
                await session.rollback()
                logger.info("Successfully rolled back session after error")
            except Exception as rollback_error:
                logger.error(f"Error during session rollback: {rollback_error}")
        raise
    finally:
        if session:
            try:
                await session.close()
                logger.debug("Database session closed succesfully")
            except Exception as close_error:
                logger.error(f"Error closing database session: {close_error}")


"""
We're gonna initialize our database connection with retry mechanism
This func is gonna verity that the database connection is working 
by attemption to connect to the database three times, with a delay of 
2 seconds between each attempt
"""


async def init_db() -> None:
    try:
        max_retries = 3
        retry_delay = 2

        # ? connect to the database with exponential backoff
        # $ Exponential backoff is a technique that increases the dely between retries exponentially
        for attempt in range(max_retries):
            try:
                async with engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info("Database connection verified successfully")
                break
            except Exception:
                if attempt == max_retries - 1:
                    logger.error(
                        f"Failed to verity database connection after {max_retries} attempts"
                    )
                    raise
                logger.warning(f"Database connection attempt {attempt + 1}")

                # ? Exponential backoff by waiting longer between each retry
                await asyncio.sleep(retry_delay * (attempt + 1))
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
