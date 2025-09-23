# Orchestrator

Controls user creation using a sine wave and an adjustable error factor.

## Run (Docker)
```bash
docker build -t orchestrator services/Orchestrator
docker run -p 8080:8000 -e USER_SIM_URL=http://0.0.0.0:8081 orchestrator

## Run (Docker Compose)
cd ..
docker compose up --build orchestrator user-simulator


# Orchestrator UI — Quick Guide (http://localhost:8080/ui)

## Controls (Sliders/Inputs)

* **Length (a.k.a. Height)** - Maximum planned users per *pulse*.
   * `height = 20` → at wave peak can spawn ~20 users simultaneously; at valley ≈ 0.
   * Average per *pulse* ≈ `0.5 × height`.

* **Width** - Duration of one wave cycle (rise-fall) in **number of pulses**.
   * Duration of 1 cycle ≈ `width × interval_ms`.
   * Example: `width=24`, `interval=500 ms` → ±**12 seconds** per cycle.

* **error_factor** - Controls the "chaos" of simulated user behavior.
   * `0.0` = orderly (safe for integration tests).
   * Higher values increase chance of erratic behavior (long seeks, "unknown" video IDs, etc.).
   * Suggestion: for demos, start with `0.0 – 0.2`.

**Rough formula to estimate concurrency:**
concurrency ≈ (0.5 × height) × (1000 / interval_ms) × avg_session_seconds

## Buttons (Functions)

* **Save Config** - Saves `height / width / error_factor` values to Orchestrator. Applied to next pulse and current/upcoming loops.

* **Pulse Once** - Executes **one** spawn cycle immediately (without waiting for loop interval).
   * Can be clicked multiple times; each click recalculates *planned users* according to current wave and calls UserSimulator accordingly.
   * Useful for **smoke testing** before starting the loop.

* **Set Interval** - Sets `interval_ms` (time gap between pulses in the loop). Lower values = more frequent spawning.

* **Start** - Activates **background loop** that auto-pulses every `interval_ms`. Continues running until Stopped or process is killed.

* **Stop** - Stops the background loop. Does not affect already running sessions; only prevents new pulses.

* **Status** - Shows current loop status: `running: true/false` and active `interval_ms`.

## Quick Tips

* Start with `height=8`, `width=24`, `interval=500 ms`, `error_factor=0.0`.
* For more activity: increase **height** or decrease **interval_ms**.
* For faster wave rise-fall: decrease **width**.
* When seeing **no user increase**:
   * Try **Pulse Once** first to ensure Orchestrator → UserSimulator path is healthy.
   * Ensure `USER_SIM_URL` is correct (inter-container use service name & internal port).
   * Keep `error_factor` low during integration (high values can trigger strict server validation).


# Scaling Strategy (Overview)

## Current scope (Milestone 2)

This service uses a single-process `asyncio` loop to "pulse" user creation with a sine-wave pattern. It's simple and perfect for a functional demo, but it's **not** meant for high scale or HA.

### Known limits of the current loop

* Single instance; no durability or retries if the process crashes.
* No backpressure; bursts are limited by one event loop.
* Live config is in-memory (not shared across replicas).

The current `asyncio` loop is intentionally minimal for the interview milestone. For real load, switch to a **queue-backed orchestrator** with **autoscaling workers**, **durable event ingress**, and **centralized config & idempotency**. This keeps the same external behavior (sine-wave user generation) while removing single-process bottlenecks.

## Production path

* **Queue-based orchestrator:** Move `pulse` to a job queue (e.g., Celery/RQ + Redis/RabbitMQ). Beat/Scheduler enqueues `pulse`; workers process it with **retries/backoff** and **at-least-once** delivery. Keep idempotency by `tick_id`.
* **Observability:** Expose Prometheus metrics (planned vs spawned, spawn latency, queue depth, error rate). Provide dashboards and alerts aligned to SLOs.