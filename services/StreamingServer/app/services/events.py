import json, sys, time, threading
from typing import Dict, Any

class EventEmitter:
    def __init__(self, filepath: str = "/app/events.log"):
        self.filepath = filepath
        self._lock = threading.Lock()
        self._emitted = 0

    @property
    def emitted(self) -> int:
        return self._emitted

    def emit(self, event: Dict[str, Any]):
        event.setdefault("ts", int(time.time()))
        line = json.dumps(event, ensure_ascii=False)
        # stdout
        print(line, file=sys.stdout, flush=True)
        # file JSONL
        with self._lock:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            self._emitted += 1