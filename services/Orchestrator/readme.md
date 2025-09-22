# Orchestrator

Controls user creation using a sine wave and an adjustable error factor.

## Run (Docker)
```bash
docker build -t orchestrator services/Orchestrator
docker run -p 8080:8080 -e USER_SIM_URL=http://host.docker.internal:8081 orchestrator
