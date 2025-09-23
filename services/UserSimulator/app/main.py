import random, time
from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.services.user import simulate_session

app = FastAPI(title="User Simulator")

ACTIONS = ["video_start", "video_pause", "video_resume", "seek", "page_leave", "session_end"]

class SimIn(BaseModel):
    error_factor: float = 0.0

@app.get("/")
def root():
    return {"service": "user-simulator"}

@app.post("/simulate")
def simulate(request:Request, inp: SimIn):
    return simulate_session(inp.error_factor)
