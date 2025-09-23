from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TICK_SECONDS: int = 10            # heartbeat interval while playing
    NODE_CAPACITY: int = 100          # sessions per node
    SCALE_UP_THRESHOLD: float = 0.8   # if any node > 80% -> add node
    SCALE_DOWN_THRESHOLD: float = 0.3 # if global < 30% for cooldown window -> remove a node
    SCALE_DOWN_COOLDOWN_S: int = 60

settings = Settings()