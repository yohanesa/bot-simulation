import json
import logging
import sys
from typing import Any, Dict
from app.core.settings import settings

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        # Add any extra fields attached via logger.bind-like pattern
        for k, v in record.__dict__.items():
            if k not in payload and k not in ("msg", "args", "levelno", "levelname",
                                              "pathname", "filename", "module", "exc_info",
                                              "exc_text", "stack_info", "lineno", "funcName",
                                              "created", "msecs", "relativeCreated", "thread",
                                              "threadName", "processName", "process"):
                payload[k] = v
        return json.dumps(payload, ensure_ascii=False)

def setup_logging() -> None:
    root = logging.getLogger()
    # Clear existing handlers so uvicorn/basicConfig don’t double-print
    for h in list(root.handlers):
        root.removeHandler(h)

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_format.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Make common noisy libs less chatty (tune if needed)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
