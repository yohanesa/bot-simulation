from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import asyncio
from typing import Optional

router = APIRouter(prefix="/loop", tags=["loop"])

def _ensure_state(app):
    if not hasattr(app.state, "loop_task"):
        app.state.loop_task = None
    if not hasattr(app.state, "loop_interval_ms"):
        app.state.loop_interval_ms = 1000 # default 1s
    if not hasattr(app.state, "pulse_once"):
        # main will set this to callable: async def pulse_once(): ...
        raise RuntimeError("app.state.pulse_once not bound. Bind it in startup.")

async def _run_loop(app):
    try:
        while True:
            await app.state.pulse_once() # one pulse
            await asyncio.sleep(app.state.loop_interval_ms / 1000)
    except asyncio.CancelledError:
        # graceful stop 
        pass


@router.post("/start")
async def start_loop(request: Request):
    app = request.app
    _ensure_state(app)
    if app.state.loop_task and not app.state.loop_task.done():
        raise HTTPException(status_code=409, detail="Loop already running")
    app.state.loop_task = asyncio.create_task(_run_loop(app))
    return {"ok": True, "message": "Loop started", "interval_ms": app.state.loop_interval_ms}


@router.post("/stop")
async def stop_loop(request: Request):
    app = request.app
    _ensure_state(app)
    task = app.state.loop_task
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        app.state.loop_task = None
        return {"ok": True, "message": "Loop stopped"}
    return JSONResponse({"ok": True, "message": "Loop was not running"}, status_code=200)


@router.get("/status")
async def loop_status(request: Request):
    app = request.app
    _ensure_state(app)
    running = app.state.loop_task is not None and not app.state.loop_task.done()
    return {
        "running": running,
        "interval_ms": app.state.loop_interval_ms,
    }


@router.post("/interval")
async def set_interval(request: Request, interval_ms: int):
    app = request.app
    _ensure_state(app)
    if interval_ms < 100:
        raise HTTPException(status_code=400, detail="interval_ms must be >= 100")
    app.state.loop_interval_ms = interval_ms
    return {"ok": True, "interval_ms": interval_ms}