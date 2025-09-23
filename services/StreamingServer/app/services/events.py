from typing import Dict, Any
import json, sys, time, threading, queue, requests, os

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



class FileEmitter:
    def __init__(self, filepath="/app/events.log"):
        self.filepath = filepath
        self._lock = threading.Lock()
        self._emitted = 0
    @property
    def emitted(self): return self._emitted
    def emit(self, event: dict):
        event.setdefault("ts", int(time.time()))
        line = json.dumps(event, ensure_ascii=False)
        print(line, file=sys.stdout, flush=True)
        with self._lock:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            self._emitted += 1

class HttpBatchEmitter:
    def __init__(self, base_url: str, batch_max=200, flush_ms=1000, token=None):
        self.base_url = base_url.rstrip("/")
        self.batch_max = batch_max
        self.flush_ms = flush_ms/1000.0
        self.token = token
        self.q = queue.Queue()
        self._emitted = 0
        self._stop = False
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
    @property
    def emitted(self): return self._emitted
    def emit(self, event: dict):
        event.setdefault("ts", int(time.time()))
        self.q.put(event)
    def _loop(self):
        buf = []
        last = time.time()
        while not self._stop:
            try:
                item = self.q.get(timeout=self.flush_ms)
                buf.append(item)
            except queue.Empty:
                pass
            now = time.time()
            if buf and (len(buf) >= self.batch_max or now - last >= self.flush_ms):
                try:
                    headers = {"Content-Type":"application/json"}
                    if self.token: headers["Authorization"] = f"Bearer {self.token}"
                    requests.post(f"{self.base_url}/events/batch", json=buf, headers=headers, timeout=3)
                    self._emitted += len(buf)
                except Exception:
                    print("Error in post data (batch)")
                    pass
                buf, last = [], now

class MultiEmitter:
    def __init__(self, file_emitter: FileEmitter, http_emitter: HttpBatchEmitter | None):
        self.file = file_emitter
        self.http = http_emitter
    @property
    def emitted(self): return (self.file.emitted) + (self.http.emitted if self.http else 0)
    def emit(self, event: dict):
        self.file.emit(event)
        if self.http: self.http.emit(event)
