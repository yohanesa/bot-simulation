#!/usr/bin/env bash
set -euo pipefail

# ---------- Config (override via env if you like) ----------
MB_URL="${MB_URL:-http://localhost:4000}"
MB_ADMIN_EMAIL="${MB_ADMIN_EMAIL:-admin@example.com}"
MB_ADMIN_FIRST="${MB_ADMIN_FIRST:-Admin}"
MB_ADMIN_LAST="${MB_ADMIN_LAST:-User}"
MB_ADMIN_PASS="${MB_ADMIN_PASS:-ChangeMe123!}"

# EventStore DB connection (Metabase -> Postgres for eventstore)
ES_DB_NAME="${ES_DB_NAME:-EventStore}"
ES_DB_HOST="${ES_DB_HOST:-db}"
ES_DB_PORT="${ES_DB_PORT:-5432}"
ES_DB_DB="${ES_DB_DB:-eventstore}"
ES_DB_USER="${ES_DB_USER:-appuser}"
ES_DB_PASS="${ES_DB_PASS:-appuser}"
ES_DB_SSL="${ES_DB_SSL:-false}"

# ---------- Helpers ----------
curl_json() { curl -sS -H "Content-Type: application/json" "$@"; }
auth_header() { echo -H "X-Metabase-Session: ${MB_SESSION}"; }

echo "Waiting Metabase to be reachable at $MB_URL..."
# Health endpoint available after boot
for i in {1..120}; do
  if curl -sS "$MB_URL/api/health" | grep -q '"ok"'; then
    echo "Metabase healthy."
    break
  fi
  sleep 2
done

# 1) Get setup token
SETUP_TOKEN=$(curl -sS "$MB_URL/api/session/properties" | sed -n 's/.*"setup-token":"\([^"]*\)".*/\1/p')
if [ -z "$SETUP_TOKEN" ]; then
  echo "Failed to get setup token. Is Metabase already configured?"
fi

# 2) Complete setup (idempotent; if already setup, this will fail harmlessly)
SETUP_PAYLOAD=$(cat <<JSON
{
  "token": "$SETUP_TOKEN",
  "user": {
    "first_name": "$MB_ADMIN_FIRST",
    "last_name": "$MB_ADMIN_LAST",
    "email": "$MB_ADMIN_EMAIL",
    "password": "$MB_ADMIN_PASS"
  },
  "prefs": {
    "site_name": "Cofounderie Demo",
    "allow_track_usage": false
  },
  "database": {
    "engine": "postgres",
    "name": "$ES_DB_NAME",
    "details": {
      "host": "$ES_DB_HOST",
      "port": $ES_DB_PORT,
      "db": "$ES_DB_DB",
      "user": "$ES_DB_USER",
      "password": "$ES_DB_PASS",
      "ssl": $ES_DB_SSL
    }
  }
}
JSON
)

# Try setup, ignore if already done
PROPS=$(curl -sS "$MB_URL/api/session/properties")
SETUP_TOKEN=$(echo "$PROPS" | sed -n 's/.*"setup-token":"\([^"]*\)".*/\1/p')
ALREADY_SETUP=$(echo "$PROPS" | grep -c '"has-user-setup":true\|"is-setup":true\|"setup-token":null')

if [ "$ALREADY_SETUP" -gt 0 ] || [ -z "$SETUP_TOKEN" ]; then
  echo "Metabase already initialized; skipping /api/setup."
else
  echo "Running first-time setup…"
  curl_json -X POST "$MB_URL/api/setup" -d "$SETUP_PAYLOAD" || true
fi

# 3) Login to get session
# --- robust login (handles spaces/newlines, shows diagnostics if it fails) ---
LOGIN_JSON="$(curl -sS -H 'Content-Type: application/json' \
  -X POST "$MB_URL/api/session" \
  -d "{\"username\":\"$MB_ADMIN_EMAIL\",\"password\":\"$MB_ADMIN_PASS\"}")"

# Try jq first (if installed), else Python, else POSIX sed fallback
if command -v jq >/dev/null 2>&1; then
  MB_SESSION="$(printf '%s' "$LOGIN_JSON" | jq -r '.id // empty')"
else
  MB_SESSION="$(python3 - <<'PY' 2>/dev/null || true
import json,sys
try:
    print(json.load(sys.stdin).get("id",""))
except Exception:
    print("")
PY
<<<"$LOGIN_JSON")"
  if [ -z "$MB_SESSION" ]; then
    # POSIX sed fallback (tolerant to spaces/newlines)
    MB_SESSION="$(printf '%s' "$LOGIN_JSON" \
      | tr -d '\r\n' \
      | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  fi
fi

if [ -z "$MB_SESSION" ]; then
  echo "Cannot obtain Metabase session. Check URL/creds or see response below:"
  echo "MB_URL=$MB_URL  MB_ADMIN_EMAIL=$MB_ADMIN_EMAIL"
  echo "Response from /api/session:"
  printf '%s\n' "$LOGIN_JSON"
  exit 1
fi
echo "Obtained Metabase session."

AUTH_HEADER="X-Metabase-Session: $MB_SESSION"

# 4) Find EventStore DB id (created during setup)
DBS=$(curl -sS -H "$AUTH_HEADER" "$MB_URL/api/database")
ES_DB_ID=$(echo "$DBS" | sed -n 's/.*"name":"'"$ES_DB_NAME"'","id":\([0-9]*\).*/\1/p' | head -n1)
if [ -z "$ES_DB_ID" ]; then
  echo "EventStore DB not found; creating manually…"
  CREATE_DB_PAYLOAD=$(cat <<JSON
  {
    "engine": "postgres",
    "name": "$ES_DB_NAME",
    "details": {
      "host": "$ES_DB_HOST",
      "port": $ES_DB_PORT,
      "db": "$ES_DB_DB",
      "user": "$ES_DB_USER",
      "password": "$ES_DB_PASS",
      "ssl": $ES_DB_SSL
    },
    "is_full_sync": true
  }
JSON
)
  ES_DB_ID=$(curl_json -X POST -H "$AUTH_HEADER" "$MB_URL/api/database" -d "$CREATE_DB_PAYLOAD" | sed -n 's/.*"id":\([0-9]*\).*/\1/p')
fi
echo "EventStore DB id: $ES_DB_ID"

# ---------- Helper to create a native SQL card ----------
create_card () {
  local NAME="$1"
  local DISPLAY="$2"
  local QUERY_SQL="$3"

  local CARD_PAYLOAD=$(cat <<JSON
{
  "name": "$NAME",
  "dataset_query": {
    "database": $ES_DB_ID,
    "type": "native",
    "native": {
      "query": "$QUERY_SQL"
    }
  },
  "display": "$DISPLAY",
  "collection_id": null,
  "description": null,
  "visualization_settings": {}
}
JSON
)

  curl_json -X POST -H "$AUTH_HEADER" "$MB_URL/api/card" -d "$CARD_PAYLOAD"
}

# ---------- Create cards ----------
RPM_CARD=$(create_card "RPM by event (last 2h)" "area" \
"SELECT date_trunc('minute', to_timestamp(ts)) AS minute, event, count(*) AS cnt
 FROM events
 WHERE ts >= EXTRACT(EPOCH FROM (now() - interval '2 hours'))
 GROUP BY 1,2
 ORDER BY 1;")

SESS_CARD=$(create_card "Active sessions (last 5m)" "scalar" \
"SELECT count(DISTINCT session_id) AS active_sessions
 FROM events
 WHERE ts >= EXTRACT(EPOCH FROM (now() - interval '5 minutes'));")

NODE_CARD=$(create_card "Node count (scale_* over time)" "line" \
"WITH marks AS (
  SELECT date_trunc('minute', to_timestamp(ts)) AS minute,
         sum(CASE WHEN event='scale_up' THEN 1 WHEN event='scale_down' THEN -1 ELSE 0 END) AS delta
  FROM events WHERE event IN ('scale_up','scale_down')
  GROUP BY 1
)
SELECT minute,
       sum(delta) OVER (ORDER BY minute ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS node_count
FROM marks ORDER BY minute;")

TOPV_CARD=$(create_card "Top videos (starts last 24h)" "bar" \
"SELECT video_id,
        count(*) FILTER (WHERE event='start') AS starts,
        count(*) FILTER (WHERE event='stop')  AS stops
 FROM events
 WHERE ts >= EXTRACT(EPOCH FROM (now() - interval '24 hours'))
 GROUP BY 1
 ORDER BY starts DESC
 LIMIT 10;")

DQ1_CARD=$(create_card "DQ: whitelist compliance (24h) %" "scalar" \
"SELECT 100.0 * avg(CASE WHEN event IN
 ('connect','start','pause','play','seek','stop','stream_tick_10s','scale_up','scale_down')
 THEN 1 ELSE 0 END) AS whitelist_compliance_pct
 FROM events
 WHERE ts >= EXTRACT(EPOCH FROM (now() - interval '24 hours'));")

DQ2_CARD=$(create_card "DQ: session presence compliance (24h) %" "scalar" \
"SELECT 100.0 * avg(CASE
    WHEN event IN ('scale_up','scale_down') THEN 1
    WHEN session_id IS NOT NULL THEN 1
    ELSE 0 END) AS session_presence_compliance_pct
 FROM events
 WHERE ts >= EXTRACT(EPOCH FROM (now() - interval '24 hours'));")

# Extract card IDs
get_ids () {
  echo "$1" | sed -n 's/.*"id":\([0-9]\+\).*/\1/p'
}
RPM_ID=$(get_ids "$RPM_CARD")
SESS_ID=$(get_ids "$SESS_CARD")
NODE_ID=$(get_ids "$NODE_CARD")
TOPV_ID=$(get_ids "$TOPV_CARD")
DQ1_ID=$(get_ids "$DQ1_CARD")
DQ2_ID=$(get_ids "$DQ2_CARD")

# ---------- Dashboards ----------
create_dash () {
  local NAME="$1"
  curl_json -X POST -H "$AUTH_HEADER" "$MB_URL/api/dashboard" -d "{\"name\":\"$NAME\"}"
}

add_card () {
  local DASH_ID="$1"
  local CARD_ID="$2"
  local ROW="$3"
  local COL="$4"
  local W="${5:-8}"
  local H="${6:-6}"
  curl_json -X POST -H "$AUTH_HEADER" "$MB_URL/api/dashboard/$DASH_ID/cards" \
    -d "{\"cardId\": $CARD_ID, \"row\": $ROW, \"col\": $COL, \"sizeX\": $W, \"sizeY\": $H}"
}

SYS_DASH=$(create_dash "System Load & Autoscaling")
SYS_ID=$(echo "$SYS_DASH" | sed -n 's/.*"id":\([0-9]\+\).*/\1/p')
add_card "$SYS_ID" "$RPM_ID" 0 0 12 8
add_card "$SYS_ID" "$SESS_ID" 0 12 4 4
add_card "$SYS_ID" "$NODE_ID" 8 0 16 8
add_card "$SYS_ID" "$TOPV_ID" 16 0 16 10

DQ_DASH=$(create_dash "Data Quality")
DQ_ID=$(echo "$DQ_DASH" | sed -n 's/.*"id":\([0-9]\+\).*/\1/p')
add_card "$DQ_ID" "$DQ1_ID" 0 0 8 6
add_card "$DQ_ID" "$DQ2_ID" 0 8 8 6

echo "Provisioning complete.
Dashboards:
- $MB_URL/dashboard/$SYS_ID
- $MB_URL/dashboard/$DQ_ID
"
