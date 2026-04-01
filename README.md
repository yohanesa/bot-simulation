# Video Streaming Simulation & Analytics Platform

This project simulates a large-scale video platform (similar to YouTube) to explore how user activity, streaming services, and analytics systems behave under load.

The goal is to design a system that is **scalable, observable, and easy to evolve**.

---

## What I Built

- **User Simulator**  
  Each user runs as an isolated service and generates realistic behavior (play, pause, seek, exit), producing event streams.

- **Streaming Service Cluster**  
  Simulates streaming servers with basic auto-scaling logic based on load per node.

- **Traffic Orchestrator**  
  Controls user growth using a wave pattern (ramp up/down), with adjustable load and error rate.

- **Event Pipeline & Storage**  
  Collects high-volume events and prepares them for analytics.

- **Analytics Layer**  
  Basic dashboards and metrics to monitor system behavior and data quality.

---

## Tech Stack

- **Backend:** Python (FastAPI)  
- **Simulation & Services:** Docker (multi-service setup)  
- **Event Handling:** HTTP-based event ingestion (lightweight, simple to debug)  
- **Data Storage:** Event store (e.g. PostgreSQL / ClickHouse style approach)  
- **Analytics / BI:** Open-source dashboard tool (e.g. Metabase / Superset)  

---

## Key Focus Areas

- Modular service design (low coupling, easy to extend)  
- High-volume event simulation  
- Realistic traffic patterns and failure scenarios  
- Observability through metrics and dashboards  

---

## Trade-offs & Decisions

- **HTTP instead of message queue (Kafka, etc.)**  
  Chosen for simplicity and faster development. Easier to debug, but not ideal for very high throughput or guaranteed delivery.

- **Service-per-user simulation**  
  Gives realistic isolation and concurrency behavior, but more resource-heavy compared to batching users in a single process.

- **Basic auto-scaling logic (not full Kubernetes)**  
  Keeps the system understandable and lightweight, while still demonstrating scaling concepts.

- **Event store over full data pipeline (no Spark/Flink)**  
  Focused on clarity and learning value instead of adding heavy infrastructure too early.

---

## Why I Built This

To explore how event-driven systems behave at scale, and how to design systems that can grow without constant refactoring.

---

## Notes

This is a personal project inspired by real-world streaming and analytics systems.
