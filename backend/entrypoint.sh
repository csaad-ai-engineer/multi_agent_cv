#!/bin/sh
set -e

OLLAMA_HOST="${OLLAMA_BASE_URL:-http://host.docker.internal:11434}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "Waiting for Ollama at $OLLAMA_HOST ..."
i=0
until curl -sf "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; do
  i=$((i + 1))
  if [ "$i" -ge "$MAX_RETRIES" ]; then
    echo "ERROR: Ollama not reachable at $OLLAMA_HOST after $((MAX_RETRIES * RETRY_INTERVAL))s. Is it running on the host?"
    exit 1
  fi
  echo "  attempt $i/$MAX_RETRIES — retrying in ${RETRY_INTERVAL}s..."
  sleep "$RETRY_INTERVAL"
done

echo "Ollama is up. Starting backend..."
exec uvicorn backend.api.main:app --host 0.0.0.0 --port 8001
