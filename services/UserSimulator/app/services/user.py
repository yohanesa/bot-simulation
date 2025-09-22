import random

def simulate_session(error_factor: float = 0.0):
    err = max(0.0, min(1.0, error_factor))
    video_id = f"vid-{random.randint(1, 100)}"
    session_id = f"sess-{random.randint(1, 1_000_000)}"

    events = []
    events.append({"type": "video_start", "video_id": video_id, "session_id": session_id})
    if random.random() < 0.5:
        events.append({"type": "video_pause", "video_id": video_id, "session_id": session_id})
        events.append({"type": "video_resume", "video_id": video_id, "session_id": session_id})
    if random.random() < 0.5:
        events.append({
            "type": "seek",
            "from_sec": random.randint(0, 100),
            "to_sec": random.randint(0, 100),
            "video_id": video_id,
            "session_id": session_id,
        })
    events.append({"type": "session_end", "video_id": video_id, "session_id": session_id})

    for e in events:
        if random.random() < err:
            e["video_id"] = None

    # sementara: print ke stdout (nanti ganti publish ke Pub/Sub / Ingestion API)
    print({"ok": True, "count": len(events), "session_id": session_id, "events": events})
    return {"ok": True, "count": len(events), "session_id": session_id, "events": events}