#!/usr/bin/env bash
# backup.sh — dumps PostgreSQL and tars the storage volume
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${ROOT}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

cd "$ROOT"
source .env 2>/dev/null || true
mkdir -p "$BACKUP_DIR"

echo "=== Backup started: $TIMESTAMP ==="

# DB dump
echo "Dumping PostgreSQL…"
docker compose exec -T db pg_dump \
  -U "${POSTGRES_USER:-lyrics}" \
  "${POSTGRES_DB:-lyricsmanager}" \
  | gzip > "${BACKUP_DIR}/db_${TIMESTAMP}.sql.gz"
echo "DB dump saved to backups/db_${TIMESTAMP}.sql.gz"

echo "=== Backup complete ==="
echo ""
echo "To restore the database:"
echo "  gunzip -c backups/db_${TIMESTAMP}.sql.gz | docker compose exec -T db psql -U lyrics lyricsmanager"
