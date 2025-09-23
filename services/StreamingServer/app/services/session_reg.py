import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Session:
    session_id: str
    user_id: str
    video_id: str
    position: float = 0.0
    state: str = "idle"            # idle | playing | paused | stopped
    node_id: int = -1
    tick_task: Optional[asyncio.Task] = None
    last_tick_ts: Optional[float] = None
    trace_id: Optional[str] = None


class SessionRegistry:
    """
    In-memory session store + per-session tick loop (default: 10s).
    All server-side events are emitted via `self.emitter.emit({...})`.
    """

    def __init__(self, emitter, tick_seconds: float = 10.0):
        self.map: Dict[str, Session] = {}
        self.emitter = emitter
        self.tick_seconds = tick_seconds

    # ---------- Metrics helpers ----------
    def count(self) -> int:
        return len(self.map)

    @property
    def ticks_running(self) -> int:
        return sum(1 for s in self.map.values() if s.tick_task and not s.tick_task.done())

    # ---------- Life-cycle ----------
    def create(
        self,
        session_id: str,
        user_id: str,
        video_id: str,
        node_id: int,
        position: float = 0.0,
        trace_id: Optional[str] = None,
    ) -> Session:
        sess = Session(
            session_id=session_id,
            user_id=user_id,
            video_id=video_id or "unknown",
            position=max(0.0, float(position or 0.0)),
            node_id=node_id,
            trace_id=trace_id,
            state="idle",
        )
        self.map[session_id] = sess
        self._emit(
            "stream_start",
            sess,
            extra={"position": sess.position},
        )
        return sess

    async def remove(self, session_id: str):
        sess = self.map.get(session_id)
        if not sess:
            return
        await self._stop_tick(sess)
        self._emit("stream_end", sess, extra={"position": sess.position})
        self.map.pop(session_id, None)

    # ---------- Actions ----------
    async def play(self, session_id: str, position: float | None = None):
        sess = self._must_get(session_id)
        if position is not None:
            sess.position = max(0.0, float(position))
        prev = sess.state
        sess.state = "playing"
        self._emit("stream_play", sess, extra={"position": sess.position, "prev_state": prev})
        await self._ensure_tick(sess)

    async def pause(self, session_id: str):
        sess = self._must_get(session_id)
        prev = sess.state
        sess.state = "paused"
        self._emit("stream_pause", sess, extra={"position": sess.position, "prev_state": prev})

    async def seek(self, session_id: str, to_position: float):
        sess = self._must_get(session_id)
        to = max(0.0, float(to_position or 0.0))
        prev_pos = sess.position
        sess.position = to
        self._emit("stream_seek", sess, extra={"from_position": prev_pos, "to_position": to})

    async def stop(self, session_id: str):
        sess = self._must_get(session_id)
        prev = sess.state
        sess.state = "stopped"
        self._emit("stream_stop", sess, extra={"position": sess.position, "prev_state": prev})
        await self._stop_tick(sess)

    # ---------- Internals ----------
    def _must_get(self, session_id: str) -> Session:
        sess = self.map.get(session_id)
        if not sess:
            raise KeyError(f"unknown session_id={session_id}")
        return sess
    
    def get(self, session_id: str):
        """Return Session or None (non-throwing lookup)."""
        return self.map.get(session_id)

    def exists(self, session_id: str) -> bool:
        return session_id in self.map

    def _emit(self, event: str, sess: Session, extra: Dict[str, Any] | None = None):
        payload = {
            "event": event,
            "session_id": sess.session_id,
            "user_id": sess.user_id,
            "video_id": sess.video_id,
            "node_id": sess.node_id,
            "position": sess.position,
            "trace_id": sess.trace_id,
            "ts": int(time.time()),
        }
        if extra:
            payload.update(extra)
        self.emitter.emit(payload)

    async def _ensure_tick(self, sess: Session):
        # Start a per-session tick loop if not running
        if not sess.tick_task or sess.tick_task.done():
            sess.tick_task = asyncio.create_task(self._tick_loop(sess))

    async def _stop_tick(self, sess: Session):
        t = sess.tick_task
        if t and not t.done():
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass
        sess.tick_task = None

    async def _tick_loop(self, sess: Session):
        try:
            while True:
                await asyncio.sleep(self.tick_seconds)
                sess.last_tick_ts = time.time()
                # Only emit while playing
                if sess.state == "playing":
                    # (optional) simulate playback progress
                    sess.position = max(0.0, float(sess.position) + self.tick_seconds)
                    self._emit("stream_tick_10s", sess)
        except asyncio.CancelledError:
            # graceful stop
            return
