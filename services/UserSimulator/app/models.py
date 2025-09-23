from pydantic import BaseModel, Field

class SimIn(BaseModel):
    error_factor: float = Field(0.0, ge=0.0, le=1.0)