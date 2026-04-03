#!/usr/bin/env python3
"""Seed initial rule_versions table with Phase A rules (v0.1.0).

Usage:
    export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db"
    python scripts/seed_phase_b.py
"""

import asyncio
import json
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Phase A rules — 6 incident-derived rules
PHASE_A_RULES = [
    {
        "id": "injection-001",
        "languages": ["python", "javascript", "typescript", "java", "go", "ruby"],
        "message": "[The Loop] SQL injection via concatenation. Use parameterized queries.",
        "severity": "ERROR",
        "metadata": {
            "incident_id": "injection-001",
            "category": "injection",
            "loop_url": "https://loop.oute.pro/incidents/injection-001",
        },
        "patterns": [
            {"pattern": "$DB.execute(\"...\" + $INPUT)"},
            {"pattern": "$DB.execute(\"...%s\" % $INPUT)"},
            {"pattern": "$DB.execute(f\"...{$INPUT}...\")"},
        ],
    },
    {
        "id": "injection-002",
        "languages": ["python", "javascript", "typescript", "ruby"],
        "message": "[The Loop] eval() with dynamic input. Use ast.literal_eval() instead.",
        "severity": "ERROR",
        "metadata": {
            "incident_id": "injection-002",
            "category": "injection",
            "loop_url": "https://loop.oute.pro/incidents/injection-002",
        },
        "patterns": [
            {"pattern": "eval($INPUT)"},
            {"pattern": "exec($INPUT)"},
        ],
    },
    {
        "id": "unsafe-api-usage-001",
        "languages": ["python"],
        "message": "[The Loop] Shell injection via shell=True. Use subprocess with argument list.",
        "severity": "ERROR",
        "metadata": {
            "incident_id": "unsafe-api-usage-001",
            "category": "unsafe-api-usage",
            "loop_url": "https://loop.oute.pro/incidents/unsafe-api-usage-001",
        },
        "patterns": [
            {"pattern": "os.system($CMD)"},
            {"pattern": "subprocess.call($CMD, ..., shell=True)"},
            {"pattern": "subprocess.run($CMD, ..., shell=True)"},
        ],
    },
    {
        "id": "missing-safety-check-001",
        "languages": ["generic"],
        "message": "[The Loop] Hardcoded secret/credential. Use os.environ.get() or Secret Manager.",
        "severity": "ERROR",
        "metadata": {
            "incident_id": "missing-safety-check-001",
            "category": "missing-safety-check",
            "loop_url": "https://loop.oute.pro/incidents/missing-safety-check-001",
        },
        "patterns": [
            {"pattern_regex": "(?i)password\\s*[:=]\\s*['\"]"},
            {"pattern_regex": "(?i)api_key\\s*[:=]\\s*['\"]"},
            {"pattern_regex": "(?i)secret\\s*[:=]\\s*['\"]"},
        ],
    },
    {
        "id": "missing-error-handling-001",
        "languages": ["python"],
        "message": "[The Loop] Bare except clause. Use specific exceptions + logging.",
        "severity": "WARNING",
        "metadata": {
            "incident_id": "missing-error-handling-001",
            "category": "missing-error-handling",
            "loop_url": "https://loop.oute.pro/incidents/missing-error-handling-001",
        },
        "patterns": [
            {"pattern": "try:\n    ...\nexcept:\n    pass"},
        ],
    },
    {
        "id": "unsafe-regex-001",
        "languages": ["python", "javascript", "java"],
        "message": "[The Loop] Regex ReDoS pattern. Rewrite without nested quantifiers.",
        "severity": "WARNING",
        "metadata": {
            "incident_id": "unsafe-regex-001",
            "category": "unsafe-regex",
            "loop_url": "https://loop.oute.pro/incidents/unsafe-regex-001",
        },
        "patterns": [
            {"pattern_regex": "\\(([.a-zA-Z]+)[*+]\\)[*+]"},
        ],
    },
]


async def seed_v0_1_0(database_url: str) -> None:
    """Seed rule_versions table with v0.1.0 and 6 Phase A rules."""
    engine = create_async_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if v0.1.0 already exists
        result = await session.execute(
            text("SELECT COUNT(*) FROM rule_versions WHERE version = '0.1.0'")
        )
        count = result.scalar()
        if count > 0:
            print("✓ v0.1.0 already seeded, skipping")
            return

        # Insert v0.1.0
        published_by = uuid4()
        rules_json = json.dumps(PHASE_A_RULES)

        stmt = text(
            """
            INSERT INTO rule_versions (id, version, rules_json, status, created_at, published_by, notes)
            VALUES (gen_random_uuid(), '0.1.0', :rules_json::jsonb, 'active', now(), :published_by, :notes)
            """
        )
        await session.execute(
            stmt,
            {
                "rules_json": rules_json,
                "published_by": str(published_by),
                "notes": "Initial Phase A rules (6 incident-derived patterns)",
            },
        )
        await session.commit()

        print(f"✓ Seeded v0.1.0 with {len(PHASE_A_RULES)} rules")
        print(f"  published_by: {published_by}")
        print(f"  status: active")


async def main() -> None:
    import os

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL env var not set")
        raise SystemExit(1)

    print(f"Seeding {database_url.split('@')[1]}")
    await seed_v0_1_0(database_url)
    print("✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
