#!/usr/bin/env bash
set -euo pipefail

# 1) Start core services (db, event-store, orchestrator, metabase)
docker compose up -d db event-store orchestrator metabase

# 2) Wait for DB
./scripts/wait-for.sh localhost 5432 90 || ./scripts/wait-for.sh db 5432 90

# 3) Seed sanity (optional check)
echo "Checking events table (ok if empty on first run)…"
docker compose exec -T db psql -U events -d events -c "SELECT to_regclass('public.events');" || true

# 4) Wait & provision Metabase (admin + datasource + dashboards)
./scripts/provision_metabase.sh

echo "All set!
- Orchestrator:  http://localhost:8080/ui
- EventStore:    http://localhost:8083/dash (or your existing endpoints)
- Metabase:      http://localhost:3000
  (Admin: admin@example.com / ChangeMe123! — change in scripts/provision_metabase.sh)
"
