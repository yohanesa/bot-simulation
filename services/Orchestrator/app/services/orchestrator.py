from dataclasses import dataclass
import math
import random
import httpx

@dataclass
class OrchestratorConfig:
    height: int = 5
    width: int = 10
    error_factor: float = 0.0  # 0..1

class OrchestratorService:
    def __init__(self):
        self.cfg = OrchestratorConfig()
        self.tick = 0
        self.spawned_total = 0
        self.user_sim_url = "http://0.0.0.0:8000/simulate"  # env or settings

    def set_config(self, height: int, width: int, error_factor: float):
        self.cfg.height = max(1, int(height))
        self.cfg.width = max(1, int(width))
        self.cfg.error_factor = max(0.0, min(1.0, float(error_factor)))

    def get_config(self):
        return self.cfg.__dict__

    def get_state(self):
        return {
            "tick": self.tick,
            "spawned_total": self.spawned_total,
            "config": self.get_config(),
        }

    def _planned_users(self) -> int:
        # simple sine window: vary by tick within width
        phase = (self.tick % self.cfg.width) / self.cfg.width
        amp = (math.sin(2 * math.pi * phase) + 1) / 2  # 0..1
        return max(0, int(round(amp * self.cfg.height)))

    async def pulse_once(self):
        planned = self._planned_users()
        spawned = 0
        async with httpx.AsyncClient(timeout=5.0) as client:
            for _ in range(planned):
                payload = {"error_factor": self.cfg.error_factor}
                try:
                    resp = await client.post(self.user_sim_url, json=payload)
                    resp.raise_for_status()
                    spawned += 1
                except Exception:
                    # TODO: log; you can increment error counters here
                    pass
        self.tick += 1
        self.spawned_total += spawned
        return {"planned": planned, "spawned": spawned, "tick": self.tick}