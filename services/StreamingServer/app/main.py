import os
import asyncio, time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.api import router as api_router
from app.routers.admin import router as admin_router
from app.routers.admin_ui import router as admin_ui_router
from app.routers.admin_diag import router as admin_diag_router
from app.services.cluster import Cluster
from app.services.events import FileEmitter, HttpBatchEmitter, MultiEmitter
from app.services.session_reg import SessionRegistry 


app = FastAPI(title="StreamingServer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(admin_router)
app.include_router(admin_ui_router)
app.include_router(admin_diag_router)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

# background autoscaler task
async def _autoscale_loop(app: FastAPI):
    try:
        while True:
            now = time.time()
            app.state.cluster.autoscale_once(now)
            await asyncio.sleep(2)
    except asyncio.CancelledError:
        pass

@app.on_event("startup")
async def _startup():
    # 1) Emitter (file + optional HTTP to EventStore)
    if not hasattr(app.state, "emitter"):
        file_em = FileEmitter()
        evt_url  = os.getenv("EVENT_STORE_URL")             # e.g. http://event-store:8000
        batchmax = int(os.getenv("EVENT_BATCH_MAX", "200"))
        flushms  = int(os.getenv("EVENT_FLUSH_MS", "1000"))
        token    = os.getenv("INGEST_TOKEN")                # optional
        http_em  = HttpBatchEmitter(evt_url, batchmax, flushms, token) if evt_url else None
        app.state.emitter = MultiEmitter(file_em, http_em)

    # 2) Cluster
    if not hasattr(app.state, "cluster"):
        app.state.cluster = Cluster(app.state.emitter) 

    # 3) Sessions
    if not hasattr(app.state, "sessions"):
        app.state.sessions = SessionRegistry(emitter=app.state.emitter, tick_seconds=10.0)

@app.on_event("shutdown")
async def _shutdown():
    if getattr(app.state, "autoscaler", None):
        app.state.autoscaler.cancel()
        try:
            await app.state.autoscaler
        except Exception:
            pass
    # cancel all session tick tasks
    for sess in list(app.state.sessions.map.values()):
        if sess.tick_task and not sess.tick_task.done():
            sess.tick_task.cancel()