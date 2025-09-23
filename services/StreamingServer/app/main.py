import asyncio, time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.api import router as api_router
from .routers.admin import router as admin_router
from .routers.admin_ui import router as admin_ui_router
from .services.events import EventEmitter
from .services.cluster import Cluster
from .services.sessions import Sessions
from .core.settings import settings

app = FastAPI(title="StreamingServer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(admin_router)
app.include_router(admin_ui_router)

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
    app.state.emitter = EventEmitter()
    app.state.cluster = Cluster(app.state.emitter)
    app.state.sessions = Sessions(app.state.emitter, tick_seconds=settings.TICK_SECONDS)
    app.state.autoscaler = asyncio.create_task(_autoscale_loop(app))

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