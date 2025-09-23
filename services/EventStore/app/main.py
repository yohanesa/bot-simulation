from fastapi import FastAPI
from .db import engine
from .models import Base
from .routers.ingest import router as ingest_router
from .routers.stats import router as stats_router
from .routers.dash import router as dash_router

app = FastAPI(title="EventStore")
app.include_router(ingest_router)
app.include_router(stats_router)
app.include_router(dash_router)

@app.on_event("startup")
def _init():
    Base.metadata.create_all(bind=engine)

@app.get("/healthz")
def healthz():
    return {"ok": True}
