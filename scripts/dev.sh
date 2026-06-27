#!/usr/bin/env bash
#
# Start the SentinelBrief dev stack in one terminal:
#   - Python ai-service (via uv) on :8000
#   - C# gateway on :8080
# then seed the demo corpus. Press Ctrl-C to stop everything cleanly.
#
# This assumes the local infrastructure is already running:
#   - Ollama on :11434   (e.g. `ollama serve`)
#   - Qdrant on :6333    (e.g. `docker compose up -d qdrant`)
#
# Usage:  ./scripts/dev.sh
#
# Works on macOS (bash 3.2) and Linux. Avoids bash 4+ features.

set -euo pipefail
set -m  # job control: each background server gets its own process group

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AI_PORT=8000
WEB_PORT=8080
AI_URL="http://localhost:${AI_PORT}"
WEB_URL="http://localhost:${WEB_PORT}"

AI_PID=""
WEB_PID=""

cleanup() {
  echo ""
  echo "Shutting down..."
  # Negative PID targets the whole process group (kills uvicorn / dotnet children too).
  [ -n "$WEB_PID" ] && kill -TERM -- -"$WEB_PID" 2>/dev/null || true
  [ -n "$AI_PID" ] && kill -TERM -- -"$AI_PID" 2>/dev/null || true
  wait 2>/dev/null || true
  echo "Stopped."
}
trap 'exit 130' INT TERM
trap cleanup EXIT

check() {  # name url
  if curl -sf "$2" >/dev/null 2>&1; then
    echo "  + $1 reachable"
  else
    echo "  ! $1 NOT reachable at $2 (start it, or answers will fail with 502)"
  fi
}

echo "Checking local infrastructure..."
check "Ollama" "http://localhost:11434/api/tags"
check "Qdrant" "http://localhost:6333/collections"

echo "Starting ai-service (uv) on ${AI_PORT}..."
( cd "$ROOT/src/ai-service" && exec uv run uvicorn app.main:app --port "$AI_PORT" ) &
AI_PID=$!

echo "Starting C# gateway on ${WEB_PORT}..."
( cd "$ROOT/src/web-api" \
    && AI_SERVICE_URL="$AI_URL" ASPNETCORE_URLS="$WEB_URL" \
       exec dotnet run --project SentinelBrief.WebApi ) &
WEB_PID=$!

printf "Waiting for services to be ready"
ready=""
for _ in $(seq 1 120); do
  if curl -sf "${AI_URL}/health" >/dev/null 2>&1 \
     && curl -sf "${WEB_URL}/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  printf "."
  sleep 1
done
echo ""

if [ "$ready" != "1" ]; then
  echo "Services did not become ready in time. See the logs above." >&2
  exit 1
fi

echo "Seeding demo corpus..."
( cd "$ROOT" && uv run --project src/ai-service python scripts/seed_demo.py "$WEB_URL" ) \
  || echo "  ! seeding failed (you can re-run scripts/seed_demo.py later)"

echo ""
echo "--------------------------------------------"
echo "  SentinelBrief is up:"
echo "    Demo page  : ${WEB_URL}"
echo "    API docs   : ${AI_URL}/docs"
echo "  Press Ctrl-C to stop everything."
echo "--------------------------------------------"

wait
