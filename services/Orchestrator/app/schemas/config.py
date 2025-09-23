from pydantic import BaseModel

class ConfigIn(BaseModel):
    height: int | None = None
    width: int | None = None
    error_factor: float | None = None