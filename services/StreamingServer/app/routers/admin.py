from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/nodes")
async def nodes():
    return {"nodes": []}

@router.get("/metrics")
async def metrics():
    return {"active_sessions": 0, "nodes": 0, "events_emitted": 0}
