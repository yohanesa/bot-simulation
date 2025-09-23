from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .core.settings import settings

# Engine with connection health-check & small pool
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)

# Request-scoped session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)
