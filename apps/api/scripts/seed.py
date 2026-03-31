"""Seed script — inserts randomized incident records for performance testing.

Usage:
    cd apps/api
    python scripts/seed.py --count 10000
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Bootstrap src module path
sys.path.insert(0, ".")

from src.config import settings  # noqa: E402
from src.adapters.postgres.models import IncidentRow  # noqa: E402

CATEGORIES = [
    "unsafe-regex",
    "injection",
    "deployment-error",
    "missing-safety-check",
    "race-condition",
    "unsafe-api-usage",
    "resource-exhaustion",
    "data-consistency",
    "missing-error-handling",
    "cascading-failure",
    "authentication-bypass",
    "configuration-drift",
]

SEVERITIES = ["critical", "high", "medium", "low"]

LANGUAGES = ["python", "javascript", "typescript", "go", "java", "rust", "ruby", "php", "c++"]

ORGS = ["Netflix", "Uber", "Airbnb", "Meta", "Google", "Amazon", "Cloudflare", None]


def _random_incident(created_by: uuid.UUID) -> IncidentRow:
    category = random.choice(CATEGORIES)
    severity = random.choice(SEVERITIES)
    created_at = datetime.now(UTC) - timedelta(days=random.randint(0, 730))
    langs = random.sample(LANGUAGES, k=random.randint(0, 3))
    tags = random.sample(["performance", "security", "reliability", "data-loss", "timeout"], k=random.randint(0, 3))

    return IncidentRow(
        id=uuid.uuid4(),
        title=f"Incident: {category} in {random.choice(LANGUAGES)} service ({uuid.uuid4().hex[:6]})",
        date=created_at.date() if random.random() > 0.3 else None,
        source_url=f"https://example.com/incidents/{uuid.uuid4().hex[:8]}" if random.random() > 0.5 else None,
        organization=random.choice(ORGS),
        category=category,
        subcategory=f"{category}-variant" if random.random() > 0.7 else None,
        failure_mode=f"Failure due to {category} pattern" if random.random() > 0.5 else None,
        severity=severity,
        affected_languages=langs,
        anti_pattern=f"Anti-pattern example for {category}. This is a longer description of the problematic code pattern that caused the incident.",
        code_example=f"# Example\nvalue = some_function(input)  # {category}" if random.random() > 0.6 else None,
        remediation=f"To fix this {category} issue: validate inputs, use safe alternatives, add monitoring.",
        static_rule_possible=random.random() > 0.5,
        semgrep_rule_id=None,
        embedding=None,
        tags=tags,
        version=1,
        deleted_at=None,
        created_at=created_at,
        updated_at=created_at,
        created_by=created_by,
    )


async def seed(count: int) -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    created_by = uuid.uuid4()
    batch_size = 500
    total_inserted = 0

    async with session_factory() as session:
        for batch_start in range(0, count, batch_size):
            batch_count = min(batch_size, count - batch_start)
            rows = [_random_incident(created_by) for _ in range(batch_count)]
            session.add_all(rows)
            await session.commit()
            total_inserted += batch_count
            print(f"Inserted {total_inserted}/{count} incidents...", flush=True)

    await engine.dispose()
    print(f"Done. {total_inserted} incidents seeded.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed incident records")
    parser.add_argument("--count", type=int, default=100, help="Number of records to insert")
    args = parser.parse_args()
    asyncio.run(seed(args.count))


if __name__ == "__main__":
    main()
