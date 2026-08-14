import logging
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

logger = logging.getLogger("rentscout.db")

LOCAL_DEFAULT = "postgresql://localhost/rentscout"

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Convenient locally, useless in a container: "localhost" there is the
    # container itself, so this surfaces as a bare "Connection refused" and a
    # long SQLAlchemy traceback that says nothing about the real cause.
    logger.warning(
        "DATABASE_URL is not set — falling back to %s. That default only "
        "works on a machine running Postgres locally. If you are on a hosting "
        "platform, set DATABASE_URL to point at your database service.",
        LOCAL_DEFAULT,
    )
    DATABASE_URL = LOCAL_DEFAULT

# Railway, Heroku and others hand out URLs starting with "postgres://", which
# SQLAlchemy 2 no longer recognises as a dialect.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    # Managed Postgres drops idle connections; without this the first request
    # after a quiet period fails on a stale socket.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """FastAPI dependency: yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
