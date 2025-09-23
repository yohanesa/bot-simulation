import httpx
from app.core.settings import settings
from app.core.loggers import get_logger

logger = get_logger("services.usersim")

class UserSimService:
    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = base_url or settings.user_sim_url
        self.timeout = timeout or settings.http_timeout

    def simulate(self, error_factor: float) -> bool:
        url = f"{self.base_url}/simulate"
        try:
            with httpx.Client(timeout=self.timeout) as c:
                r = c.post(url, json={"error_factor": error_factor})
                ok = r.status_code == 200
                if ok:
                    logger.debug("UserSim simulate OK", extra={"url": url, "status": r.status_code})
                else:
                    logger.warning("UserSim simulate non-200",
                                   extra={"url": url, "status": r.status_code, "body": r.text[:200]})
                return ok
        except httpx.TimeoutException:
            logger.error("UserSim timeout", extra={"url": url, "timeout": self.timeout})
            return False
        except Exception as e:
            logger.exception("UserSim request failed", extra={"url": url, "error_factor": error_factor})
            return False

usersim = UserSimService()
