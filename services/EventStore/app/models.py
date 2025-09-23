from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, BigInteger, JSON, Index
import uuid, datetime as dt

class Base(DeclarativeBase): pass

def now_ts() -> int: return int(dt.datetime.utcnow().timestamp())

class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ts: Mapped[int] = mapped_column(BigInteger, index=True, default=now_ts)
    event: Mapped[str] = mapped_column(String(64), index=True)

    # ⬇️ make session-scoped fields optional (nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    user_id:    Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    video_id:   Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)

    node_id:  Mapped[int] = mapped_column(Integer)
    position: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    attrs: Mapped[dict | None] = mapped_column(JSON, nullable=True)

Index("ix_events_ts_event", Event.ts, Event.event)
Index("ix_events_video_ts", Event.video_id, Event.ts)


# simple minute rollup (MVP)
class RollupMinute(Base):
    __tablename__ = "rollup_minute"
    bucket_ts: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # minute epoch
    event: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
