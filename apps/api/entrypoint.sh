#!/bin/bash
set -e

echo "🗄️  Running database migrations..."
echo "   Database URL: ${DATABASE_URL:0:20}... (redacted)"

if [ -z "$DATABASE_URL" ]; then
  echo "❌ ERROR: DATABASE_URL not set. Skipping migrations."
  echo "   API will start but rule versions may be incomplete."
else
  if ! command -v alembic &> /dev/null; then
    echo "❌ ERROR: alembic command not found"
    exit 1
  fi

  echo "   Running: alembic upgrade head"
  if alembic upgrade head; then
    echo "✅ Migrations completed successfully"
  else
    echo "⚠️  Migrations exited with code $?, but continuing startup..."
  fi
fi

echo "🚀 Starting API server on port $PORT..."
exec uvicorn src.main:app --host 0.0.0.0 --port $PORT
