#!/usr/bin/env python3
"""Standalone migration runner for Cloud SQL."""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

async def run_migrations():
    """Run Alembic migrations asynchronously."""
    import subprocess

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return False

    # Convert asyncpg URL to psycopg URL for alembic
    alembic_url = db_url.replace("+asyncpg", "")

    print(f"Running migrations with: {alembic_url[:50]}...")

    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=str(Path(__file__).parent),
        env={**os.environ, "DATABASE_URL": alembic_url},
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode == 0

if __name__ == "__main__":
    success = asyncio.run(run_migrations())
    sys.exit(0 if success else 1)
