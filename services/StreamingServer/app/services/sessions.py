import asyncio, time
from dataclasses import dataclass, field
from typing import Dict, Optional
from .events import EventEmitter

@dataclass
class Session:
    session_id: str
    user_id: str
    video_id: str
    position: float = 0.0
    state: str = "idle"  # idle|playing|paused|stopped
    node_id: int = -1
    tick_task: Optional[asyncio.Task] = None
    last_tick_ts: Optional[float] = None

class Sessions:
    def __init__(self, emitter: EventEmitter, tick_seconds: int = 10):
        self.map: Dict[str, Session] = {}
        self.emitter = emitter
        self.tick_seconds = tick_seconds

    def create(self, session_id: str, user_id: str, video_id: str, node_id: int, position: float = 0.0) -> Session:
        sess = Session(session_id=session_id, user_id=user_id, video_id=video_id, position=position, node_id=node_id)
        self.map[session_id] = sess
        self.emitter.emit({
            "event": "stream_start", "session_id": session_id, "user_id": user_id,
            "video_id": video_id, "position": position, "node_id": node_id
        })
        return sess

    def get(self, session_id: str) -> Optional[Session]:
        return self.map.get(session_id)

    def remove(self, session_id: str):
        sess = self.map.pop(session_id, None)
        if sess and sess.tick_task and not sess.tick_task.done():
            sess.tick_task.cancel()
        return sess

    async def _tick_loop(self, sess: Session):
        try:
            while sess.state == "playing":
                await asyncio.sleep(self.tick_seconds)
                sess.last_tick_ts = time.time()
                self.emitter.emit({
                    "event": "stream_tick_10s", "session_id": sess.session_id,
                    "user_id": sess.user_id, "video_id": sess.video_id,
                    "position": sess.position, "node_id": sess.node_id
                })
        except asyncio.CancelledError:
            pass

    def _ensure_tick(self, sess: Session):
        # start tick loop if playing and no task
        if sess.state == "playing" and (not sess.tick_task or sess.tick_task.done()):
            sess.tick_task = asyncio.create_task(self._tick_loop(sess))

    def play(self, session_id: str, position: Optional[float] = None):
        sess = self.map[session_id]
        if position is not None:
            sess.position = position
        prev = sess.state
        sess.state = "playing"
        self.emitter.emit({
            "event": "stream_play", "session_id": sess.session_id,
            "from_state": prev, "position": sess.position, "node_id": sess.node_id
        })
        self._ensure_tick(sess)

    def pause(self, session_id: str):
        sess = self.map[session_id]
        prev = sess.state
        sess.state = "paused"
        if sess.tick_task and not sess.tick_task.done():
            sess.tick_task.cancel()
        self.emitter.emit({
            "event": "stream_pause", "session_id": sess.session_id,
            "from_state": prev, "position": sess.position, "node_id": sess.node_id
        })

    def seek(self, session_id: str, to_position: float):
        sess = self.map[session_id]
        prev_pos = sess.position
        sess.position = to_position
        self.emitter.emit({
            "event": "stream_seek", "session_id": sess.session_id,
            "from": prev_pos, "to": to_position, "node_id": sess.node_id
        })

    def stop(self, session_id: str):
        sess = self.map[session_id]
        prev = sess.state
        sess.state = "stopped"
        if sess.tick_task and not sess.tick_task.done():
            sess.tick_task.cancel()
        self.emitter.emit({
            "event": "stream_stop", "session_id": sess.session_id,
            "from_state": prev, "position": sess.position, "node_id": sess.node_id
        })