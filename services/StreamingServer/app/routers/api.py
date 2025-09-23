from fastapi import APIRouter, HTTPException, Request
from ..models.schemas import ConnectRequest, ConnectResponse, ActionRequest, DisconnectRequest

router = APIRouter(tags=["api"])

@router.post("/connect", response_model=ConnectResponse)
async def connect(req: Request, body: ConnectRequest):
    app = req.app
    if body.session_id in app.state.sessions.map:
        return ConnectResponse(ok=True, node_id=app.state.sessions.map[body.session_id].node_id, assigned=True)
    node_id = app.state.cluster.assign(body.session_id)
    app.state.sessions.create(
        session_id=body.session_id,
        user_id=body.user_id,
        video_id=body.video_id,
        node_id=node_id,
        position=body.position or 0.0,
    )
    return ConnectResponse(node_id=node_id)

@router.post("/action")
async def action(req: Request, body: ActionRequest):
    app = req.app
    sess = app.state.sessions.get(body.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="unknown session_id")

    if body.type == "play":
        app.state.sessions.play(body.session_id, position=body.position)
    elif body.type == "pause":
        app.state.sessions.pause(body.session_id)
    elif body.type == "seek":
        if body.to_position is None:
            raise HTTPException(status_code=400, detail="to_position required for seek")
        app.state.sessions.seek(body.session_id, body.to_position)
    elif body.type == "stop":
        app.state.sessions.stop(body.session_id)
    else:
        raise HTTPException(status_code=400, detail="unknown type")

    return {"ok": True}

@router.post("/disconnect")
async def disconnect(req: Request, body: DisconnectRequest):
    app = req.app
    sess = app.state.sessions.get(body.session_id)
    if not sess:
        return {"ok": True, "message": "already gone"}
    app.state.sessions.stop(body.session_id)
    app.state.sessions.remove(body.session_id)
    app.state.cluster.release(body.session_id)
    return {"ok": True}