from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import SimIn
from .services.simulator import simulate_session

app = FastAPI(title="UserSimulator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/simulate")
async def simulate(inp: SimIn):
    # Run ONE session and return a summary
    return await simulate_session(inp.error_factor)