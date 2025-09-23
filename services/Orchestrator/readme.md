# Orchestrator

Controls user creation using a sine wave and an adjustable error factor.

## Run (Docker)
```bash
docker build -t orchestrator services/Orchestrator
docker run -p 8080:8080 -e USER_SIM_URL=http://0.0.0.0:8081 orchestrator

## Run (Docker Compose)
cd ..
docker compose up --build orchestrator user-simulator


Scaling Strategy (Overview)
Current scope (Milestone 2)

This service uses a single-process asyncio loop to “pulse” user creation with a sine-wave pattern. It’s simple and perfect for a functional demo, but it’s not meant for high scale or HA.

Known limits of the current loop

Single instance; no durability or retries if the process crashes.

No backpressure; bursts are limited by one event loop.

Live config is in-memory (not shared across replicas).

The current asyncio loop is intentionally minimal for the interview milestone.
For real load, switch to a queue-backed orchestrator with autoscaling workers, durable event ingress, and centralized config & idempotency.
This keeps the same external behavior (sine-wave user generation) while removing single-process bottlenecks.

Production path

Queue-based orchestrator: Move pulse to a job queue (e.g., Celery/RQ + Redis/RabbitMQ). Beat/Scheduler enqueues pulse; workers process it with retries/backoff and at-least-once delivery. Keep idempotency by tick_id.

Observability: Expose Prometheus metrics (planned vs spawned, spawn latency, queue depth, error rate). Provide dashboards and alerts aligned to SLOs.