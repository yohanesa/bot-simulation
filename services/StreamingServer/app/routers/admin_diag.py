from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import time

router = APIRouter(prefix="/admin", tags=["admin-diag"])

@router.get("/emitter")
async def emitter_info(req: Request):
    app = req.app
    attached = hasattr(app.state, "emitter")
    cls = app.state.emitter.__class__.__name__ if attached else None
    emitted = getattr(app.state.emitter, "emitted", None) if attached else None
    return {"attached": attached, "class": cls, "emitted": emitted}

@router.post("/test/emit")
async def test_emit(req: Request):
    app = req.app
    if not hasattr(app.state, "emitter"):
        return JSONResponse({"ok": False, "error": "no emitter attached"}, status_code=500)
    app.state.emitter.emit({
        "event": "test_emit",
        "session_id": "diag",
        "user_id": "diag",
        "video_id": "diag",
        "node_id": 0,
        "position": 0.0,
        "ts": int(time.time()),
    })
    # return updated counter
    return {"ok": True, "after_emitted": getattr(app.state.emitter, "emitted", None)}
