# app/integrations/streaming.py
import httpx, os
from app.core.settings import settings
BASE = settings.STREAMING_SERVER_URL

url = f"{BASE}/connect"
print(f"Attempting to connect to: {url}")

async def server_connect(session_id, user_id, video_id, position=0.0):
    async with httpx.AsyncClient(timeout=5) as c:
        await c.post(f"{BASE}/connect", json={
            "session_id": session_id, "user_id": user_id,
            "video_id": video_id, "position": position
        })

async def server_action(session_id, type_, position=None, to_position=None):
    payload = {"session_id": session_id, "type": type_}
    if position is not None: payload["position"] = position
    if to_position is not None: payload["to_position"] = to_position
    async with httpx.AsyncClient(timeout=5) as c:
        await c.post(f"{BASE}/action", json=payload)

async def server_disconnect(session_id):
    async with httpx.AsyncClient(timeout=5) as c:
        await c.post(f"{BASE}/disconnect", json={"session_id": session_id})
