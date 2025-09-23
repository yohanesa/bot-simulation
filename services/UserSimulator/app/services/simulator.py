import asyncio, random, time, uuid
import httpx   # NEW: for catching HTTP errors
from app.integrations.streaming import server_connect, server_action, server_disconnect
from app.core.settings import settings

VIDEOS = ["video-0001","video-0002","video-0003","video-0004","video-0005"]

async def simulate_session(error_factor: float) -> dict:
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    video_id = random.choice(VIDEOS)

    # With some error_factor, send a slightly dodgy connect (but keep schema-safe)
    malformed = random.random() < error_factor * 0.15
    safe_video_id = video_id if not malformed else "unknown"   # <- was None

    errors = []  # collect, not crash

    # CONNECT
    try:
        await server_connect(session_id=session_id, user_id=user_id, video_id=safe_video_id, position=0.0)
    except httpx.HTTPError as e:
        errors.append(f"connect:{e!r}")

    # initial PLAY
    try:
        await server_action(session_id, "play", position=0.0)
    except httpx.HTTPError as e:
        errors.append(f"play:{e!r}")

    # behavior loop
    t_end = time.time() + random.randint(settings.MIN_PLAY_SEC, settings.MAX_PLAY_SEC)
    cur_pos = 0.0
    while time.time() < t_end:
        await asyncio.sleep(random.uniform(1.0, 3.0))
        cur_pos += random.uniform(1.0, 3.0)

        # pause/resume
        if random.random() < settings.PAUSE_CHANCE:
            try:
                await server_action(session_id, "pause")
                await asyncio.sleep(random.uniform(0.5, 2.0))
                await server_action(session_id, "play", position=cur_pos)
            except httpx.HTTPError as e:
                errors.append(f"pause/play:{e!r}")

        # seek (keep schema-safe)
        if random.random() < settings.SEEK_CHANCE:
            to_pos = cur_pos + random.uniform(-15.0, 45.0)
            if random.random() < error_factor * 0.1:
                to_pos = -5.0  # still inject nonsense...
            to_pos = max(0.0, to_pos)  # ...but clamp so schema stays valid
            try:
                await server_action(session_id, "seek", to_position=to_pos)
            except httpx.HTTPError as e:
                errors.append(f"seek:{e!r}")
            cur_pos = max(0.0, to_pos)

    # STOP & DISCONNECT (don’t fail the whole endpoint)
    try:
        await server_action(session_id, "stop")
    except httpx.HTTPError as e:
        errors.append(f"stop:{e!r}")
    finally:
        try:
            await server_disconnect(session_id)
        except httpx.HTTPError as e:
            errors.append(f"disconnect:{e!r}")

    return {
        "session_id": session_id,
        "user_id": user_id,
        "video_id": safe_video_id,
        "error_factor": error_factor,
        "errors": errors,  # helpful to see if anything failed
    }
