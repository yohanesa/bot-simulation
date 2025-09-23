from fastapi import APIRouter, FastAPI
from .loop import router as loop_router
from ..views import orchestrator as orch_view
from .ui import router as ui_router

# router = APIRouter()
# router.add_api_route("/", root, methods=["GET"])
# router.add_api_route("/config", set_config, methods=["POST"])
# router.add_api_route("/pulse", pulse, methods=["POST"])
api = APIRouter()
api.include_router(loop_router)
api.include_router(orch_view.router)
api.include_router(ui_router)

def setup_app(app: FastAPI):
# Bind pulse_once on startup
    @app.on_event("startup")
    async def _startup_bind():
        await orch_view.bind_pulse_once_to_app_state(app)