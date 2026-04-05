#!/bin/bash
set -e

echo "🚀 Starting API server on port $PORT..."
exec uvicorn src.main:app --host 0.0.0.0 --port $PORT
