#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

docker stop pm-app 2>/dev/null || true
docker rm pm-app 2>/dev/null || true

docker build -t pm-app "$PROJECT_DIR"
docker run -d --name pm-app -p 8000:8000 \
  --env-file "$PROJECT_DIR/.env" \
  -v "$PROJECT_DIR/data:/app/data" \
  pm-app

echo "App running at http://localhost:8000"
