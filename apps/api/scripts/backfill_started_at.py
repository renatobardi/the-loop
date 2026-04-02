"""Backfill started_at from the legacy date field for existing incidents.

Idempotent — safe to run multiple times. Only updates rows where started_at IS NULL.

Usage:
    export DATABASE_URL="postgresql+asyncpg://..."
    python scripts/backfill_started_at.py
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    # Replace asyncpg driver with psycopg2-compatible sync URL if needed
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    engine = create_engine(sync_url)

    with engine.begin() as conn:
        # Priority 1: backfill from legacy date field
        result_date = conn.execute(
            text(
                "UPDATE incidents "
                "SET started_at = CAST(date AS TIMESTAMPTZ) "
                "WHERE started_at IS NULL AND date IS NOT NULL"
            )
        )
        sys.stdout.write(f"Backfilled started_at from date: {result_date.rowcount} rows\n")

        # Priority 2: fall back to created_at for incidents with no date
        result_created = conn.execute(
            text(
                "UPDATE incidents "
                "SET started_at = created_at "
                "WHERE started_at IS NULL AND date IS NULL"
            )
        )
        sys.stdout.write(f"Backfilled started_at from created_at: {result_created.rowcount} rows\n")

    sys.stdout.write("Backfill complete.\n")


if __name__ == "__main__":
    main()
