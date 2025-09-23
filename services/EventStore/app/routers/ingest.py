from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Event, Base, RollupMinute
import math, time

router = APIRouter(prefix="/events", tags=["ingest"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def _auth(token_header: str | None, expected: str | None):
    if expected and (token_header != f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="bad token")

@router.post("")
def ingest_one(payload: dict, db: Session = Depends(get_db), authorization: str | None = Header(None)):
    from ..core.settings import settings
    _auth(authorization, settings.INGEST_TOKEN)
    ev = Event(**payload)
    db.add(ev)
    _bump_rollup(db, ev.ts, ev.event)
    db.commit()
    return {"ok": True, "id": ev.id}

@router.post("/batch")
def ingest_batch(payload: list[dict], db: Session = Depends(get_db), authorization: str | None = Header(None)):
    from ..core.settings import settings
    _auth(authorization, settings.INGEST_TOKEN)
    events = [Event(**p) for p in payload]
    db.add_all(events)
    # fast rollup: group in python
    agg = {}
    for e in events:
        bucket = int(math.floor(e.ts / 60) * 60)
        agg[(bucket, e.event)] = agg.get((bucket, e.event), 0) + 1
    for (bucket, ev), cnt in agg.items():
        db.merge(RollupMinute(bucket_ts=bucket, event=ev, count=cnt))
    db.commit()
    return {"ok": True, "n": len(events)}

def _bump_rollup(db: Session, ts: int, ev: str):
    import math
    bucket = int(math.floor(ts / 60) * 60)
    existing = db.get(RollupMinute, {"bucket_ts": bucket, "event": ev})
    if existing:
        existing.count += 1
    else:
        db.add(RollupMinute(bucket_ts=bucket, event=ev, count=1))
