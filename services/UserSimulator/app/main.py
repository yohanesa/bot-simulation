import random, time
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="User Simulator")

ACTIONS = ["video_start", "video_pause", "video_resume", "seek", "page_leave", "session_end"]

class SimIn(BaseModel):
    error_factor: float = 0.0

@app.get("/")
def root():
    return {"service": "user-simulator"}

@app.post("/simulate")
def simulate(inp: SimIn):
    """
    Simulates one user session quickly (synchronous for starter).
    Later, this will publish events to a queue.
    """
    err = max(0.0, min(1.0, inp.error_factor))
    video_id = f"vid-{random.randint(1, 100)}"
    session_id = f"sess-{random.randint(1, 1_000_000)}"

    events = []

    # start playing
    events.append({"type":"video_start","video_id":video_id,"session_id":session_id})
    # maybe a pause
    if random.random() < 0.5:
        events.append({"type":"video_pause","video_id":video_id,"session_id":session_id})
        events.append({"type":"video_resume","video_id":video_id,"session_id":session_id})
    # maybe a seek
    if random.random() < 0.5:
        events.append({"type":"seek","from_sec":random.randint(0,100),"to_sec":random.randint(0,100),
                       "video_id":video_id,"session_id":session_id})
    # end
    events.append({"type":"session_end","video_id":video_id,"session_id":session_id})

    # inject simple errors based on error_factor
    for e in events:
        if random.random() < err:
            # make an attribute erroneous
            e["video_id"] = None

    # (later: send to ingestion service; now just return)
    return {"ok": True, "count": len(events), "session_id": session_id, "events": events}
