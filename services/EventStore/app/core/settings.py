from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Example: postgresql+psycopg://USER:PASS@HOST:PORT/DB
    DATABASE_URL: str = "postgresql+psycopg://events:events@db:5432/events"
    # Optional shared-secret to protect ingest endpoints
    INGEST_TOKEN: str | None = None

settings = Settings()
