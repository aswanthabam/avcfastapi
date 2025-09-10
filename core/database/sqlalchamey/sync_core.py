# apps/database_sync.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings

_sync_engine = None
SessionLocal = None


def get_db_session():
    global _sync_engine, SessionLocal
    if _sync_engine is None:
        sync_url = settings.DATABASE_URL_SYNC
        _sync_engine = create_engine(sync_url, echo=True)
        SessionLocal = sessionmaker(
            bind=_sync_engine, autocommit=False, autoflush=False
        )
    return SessionLocal()
