from fastapi import APIRouter

router = APIRouter(tags=["api"])

@router.post("/connect")
async def connect():
    return {"ok": True}

@router.post("/action")
async def action():
    return {"ok": True}

@router.post("/disconnect")
async def disconnect():
    return {"ok": True}
