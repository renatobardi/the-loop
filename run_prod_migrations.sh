#!/bin/bash
# Run Alembic migrations in production via Cloud SQL Proxy

set -e

PROJECT_ID="theloopoute"
INSTANCE="theloopoute:southamerica-east1:theloop-db"
PORT=5433

echo "🔐 Authenticating with GCP..."
gcloud auth application-default login

echo "🔌 Starting Cloud SQL Proxy on port $PORT..."
cloud-sql-proxy $INSTANCE --port $PORT > /tmp/cloudsql.log 2>&1 &
PROXY_PID=$!
echo "  PID: $PROXY_PID"

sleep 3

echo "📦 Getting database credentials from Secret Manager..."
DB_URL=$(gcloud secrets versions access latest --secret=THELOOP_API_DATABASE_URL)

# Convert asyncpg URL to psycopg for Alembic
DB_URL="${DB_URL//+asyncpg/}"
DB_URL="${DB_URL//\?host=.*//}"  # Remove socket path
DB_URL="postgresql://postgres:theloop_dev_2026@localhost:$PORT/theloop"

echo "🗄️  Running migrations..."
echo "   Database: localhost:$PORT/theloop"

cd /Users/bardi/Projetos/the-loop/apps/api

export DATABASE_URL="$DB_URL"
export PYTHONPATH=/Users/bardi/Projetos/the-loop/apps/api:$PYTHONPATH

python3 << 'PYEOF'
import subprocess
import sys
import os

result = subprocess.run(
    ["alembic", "upgrade", "head"],
    capture_output=False,
    text=True
)

sys.exit(result.returncode)
PYEOF

MIGRATION_EXIT=$?

echo ""
echo "🛑 Stopping Cloud SQL Proxy (PID $PROXY_PID)..."
kill $PROXY_PID 2>/dev/null || true

if [ $MIGRATION_EXIT -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
    echo ""
    echo "Verifying..."
    curl -s https://api.loop.oute.pro/api/v1/rules/0.4.0 | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'  Rules in v0.4.0: {len(data.get(\"rules\", []))}')"
else
    echo "❌ Migrations failed!"
    exit 1
fi
