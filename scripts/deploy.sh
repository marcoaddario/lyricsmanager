#!/usr/bin/env bash
# deploy.sh — first-time setup and deployment helper
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

cd "$ROOT"

echo "=== Lyrics Manager Deployment ==="

# 1. Check for .env
if [ ! -f .env ]; then
  echo "Creating .env from .env.example…"
  cp .env.example .env
  # Generate a random SECRET_KEY
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(48))" 2>/dev/null || openssl rand -hex 48)
  sed -i "s|change_me_very_long_random_secret_key_at_least_64_chars|$SECRET|" .env
  echo ""
  echo "⚠  .env created. Please set POSTGRES_PASSWORD and FIRST_ADMIN_PASSWORD before continuing."
  echo "   Edit .env, then re-run this script."
  exit 0
fi

# 2. Pull / build
echo "Building images…"
docker compose build --parallel

# 3. Start
echo "Starting services…"
docker compose up -d

# 4. Wait for health
echo "Waiting for API to be healthy…"
for i in $(seq 1 30); do
  if docker compose exec -T api curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "API is healthy ✓"
    break
  fi
  sleep 2
done

echo ""
echo "=== Deployment complete ==="
echo "Application is running at http://localhost"
echo "API docs at http://localhost/api/docs"
echo ""
echo "Default admin credentials (change immediately!):"
grep FIRST_ADMIN_EMAIL .env | head -1
grep FIRST_ADMIN_PASSWORD .env | head -1
