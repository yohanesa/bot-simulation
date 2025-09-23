from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    STREAMING_SERVER_URL: str = "http://localhost:8082"
    # knobs for the simulator
    MIN_PLAY_SEC: int = 15
    MAX_PLAY_SEC: int = 60
    PAUSE_CHANCE: float = 0.25
    SEEK_CHANCE: float = 0.35

settings = Settings()