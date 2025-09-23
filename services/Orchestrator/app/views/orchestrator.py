from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.schemas.config import ConfigIn as ConfigSchema
from ..services.orchestrator import OrchestratorService

router = APIRouter()
service = OrchestratorService()


@router.post("/config")
async def set_config(cfg: ConfigSchema):
    service.set_config(height=cfg.height, width=cfg.width, error_factor=cfg.error_factor)
    return {"ok": True, "config": service.get_config()}


@router.post("/pulse")
async def pulse_once():
    result = await service.pulse_once()
    return JSONResponse(result)


@router.get("/")
async def root_state():
    return service.get_state()


# Helper to expose pulse_once to app.state in main
async def bind_pulse_once_to_app_state(app):
    async def _pulse_once():
        await service.pulse_once()
    app.state.pulse_once = _pulse_once