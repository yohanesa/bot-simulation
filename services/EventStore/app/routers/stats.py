from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import SessionLocal

router = APIRouter(prefix="/stats", tags=["stats"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/overview")
def overview(db: Session = Depends(get_db), minutes: int = 5):
    # events in last N minutes
    q = text("""
        SELECT event, COUNT(*) AS c
        FROM events
        WHERE ts >= EXTRACT(EPOCH FROM NOW())::bigint - :window
        GROUP BY event ORDER BY c DESC
    """)
    rows = db.execute(q, {"window": minutes*60}).mappings().all()
    return {"window_min": minutes, "by_event": rows}

@router.get("/top-videos")
def top_videos(db: Session = Depends(get_db), minutes: int = 60, limit: int = 10):
    q = text("""
        SELECT video_id, COUNT(*) AS c
        FROM events
        WHERE ts >= EXTRACT(EPOCH FROM NOW())::bigint - :window
        GROUP BY video_id ORDER BY c DESC LIMIT :lim
    """)
    rows = db.execute(q, {"window": minutes*60, "lim": limit}).mappings().all()
    return {"window_min": minutes, "top": rows}

@router.get("/rpm")
def rpm(db: Session = Depends(get_db), minutes: int = 30):
    q = text("""
      SELECT bucket_ts, event, SUM(count) AS c
      FROM rollup_minute
      WHERE bucket_ts >= EXTRACT(EPOCH FROM NOW())::bigint - :window
      GROUP BY bucket_ts, event ORDER BY bucket_ts ASC, event ASC
    """)
    rows = db.execute(q, {"window": minutes*60}).mappings().all()
    return {"window_min": minutes, "series": rows}
