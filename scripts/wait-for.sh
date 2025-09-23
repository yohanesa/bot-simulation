#!/usr/bin/env bash
# Minimal wait-for (port or HTTP) with timeout
set -euo pipefail

host="$1"
shift
port="$1"
shift
timeout="${1:-60}"

echo "Waiting for $host:$port (timeout ${timeout}s)..."
for i in $(seq 1 "$timeout"); do
  if (echo >/dev/tcp/$host/$port) >/dev/null 2>&1; then
    echo "Up after $i s"
    exit 0
  fi
  sleep 1
done

echo "Timed out waiting for $host:$port"
exit 1
