from fastapi import APIRouter, Request
from ..models.schemas import NodesResponse, NodeInfo, Metrics

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/nodes", response_model=NodesResponse)
async def nodes(req: Request):
    app = req.app
    snap = app.state.cluster.node_snapshot()
    return {"nodes": [NodeInfo(**n) for n in snap]}

@router.get("/metrics", response_model=Metrics)
async def metrics(req: Request):
    app = req.app
    active = len(app.state.sessions.map)
    nodes = len(app.state.cluster.nodes)
    emitted = app.state.emitter.emitted
    ticks_running = sum(1 for s in app.state.sessions.map.values() if s.tick_task and not s.tick_task.done())
    return Metrics(
        active_sessions=active,
        nodes=nodes,
        scale_up_count=app.state.cluster.scale_up_count,
        scale_down_count=app.state.cluster.scale_down_count,
        events_emitted=emitted,
        ticks_running=ticks_running,
    )