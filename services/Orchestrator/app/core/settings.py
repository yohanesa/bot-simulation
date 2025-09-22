# app/core/settings.py
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

load_dotenv()  # optional; env-file support below also works

class Settings(BaseSettings):
    app_name: str = Field("Orchestrator", alias="APP_NAME")
    user_sim_url: str = Field("http://localhost:8081", alias="USER_SIM_URL")
    http_timeout: float = Field(5.0, alias="HTTP_TIMEOUT")
    LOOP_INTERVAL_MS_DEFAULT: int = 1000

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_format: str = Field("console", alias="LOG_FORMAT")

    # pydantic-settings v2 style config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
