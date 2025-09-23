from fastapi import APIRouter, Request
from ..models.schemas import NodesResponse, NodeInfo, Metrics

router = APIRouter(prefix="/admin", tags=["admin"])

def _safe_emitted(app) -> int:
    em = getattr(app.state, "emitter", None)
    return int(getattr(em, "emitted", 0)) if em else 0

@router.get("/nodes", response_model=NodesResponse)
async def nodes(req: Request):
    app = req.app
    cluster = getattr(app.state, "cluster", None)
    if not cluster:
        return {"nodes": []}
    snap = cluster.node_snapshot()
    return {"nodes": [NodeInfo(**n) for n in snap]}

@router.get("/metrics", response_model=Metrics)
async def metrics(req: Request):
    app = req.app
    cluster  = getattr(app.state, "cluster", None)
    sessions = getattr(app.state, "sessions", None)

    active = len(getattr(sessions, "map", {})) if sessions else 0
    nodes  = len(getattr(cluster, "nodes", [])) if cluster else 0
    ticks_running = (
        sum(1 for s in getattr(sessions, "map", {}).values() if s.tick_task and not s.tick_task.done())
        if sessions else 0
    )

    return Metrics(
        active_sessions=active,
        nodes=nodes,
        scale_up_count=getattr(cluster, "scale_up_count", 0),
        scale_down_count=getattr(cluster, "scale_down_count", 0),
        events_emitted=_safe_emitted(app),
        ticks_running=ticks_running,
    )
