# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.core.settings import settings
# from app.routers.root import router as root_router

# def create_app() -> FastAPI:
#     app = FastAPI(title=settings.app_name)
#     app.include_router(root_router)
#     return app

# app = create_app()

from fastapi import FastAPI
from .routers.root import api, setup_app
from fastapi.middleware.cors import CORSMiddleware
from .core.settings import settings

app = FastAPI(title="Orchestrator")

# CORS (adjust for your dev domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _apply_defaults():
    if not hasattr(app.state, "loop_interval_ms"):
        app.state.loop_interval_ms = settings.LOOP_INTERVAL_MS_DEFAULT

@app.get("/metrics")
async def metrics():
    running = hasattr(app.state, "loop_task") and app.state.loop_task is not None and not app.state.loop_task.done()
    return {
        "loop_running": running,
        "loop_interval_ms": getattr(app.state, "loop_interval_ms", 1000),
    }

app.include_router(api)
setup_app(app)
