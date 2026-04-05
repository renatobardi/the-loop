#!/usr/bin/env python3
"""Seed analytics test data for Spec-019 validation.

Creates comprehensive test dataset across teams, categories, severities, and timelines.
Covers 52-week period with mix of resolved/unresolved incidents.

Usage:
  python3 scripts/seed_analytics_testdata.py --count 200

Environment:
  DATABASE_URL — PostgreSQL connection string (required)

Note: Run locally first to verify, then on production if needed.
      All seeded data has source='test-seed-spec019' and can be filtered/deleted.
"""

import os
import sys
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add apps/api to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)  # /Users/bardi/Projetos/the-loop
api_dir = os.path.join(repo_root, 'apps', 'api')
sys.path.insert(0, api_dir)

from src.adapters.postgres.models import IncidentRow, PostmortumRow


TEAMS = ['Backend', 'Frontend', 'DevOps', 'Platform', 'QA']
CATEGORIES = ['code_pattern', 'infrastructure', 'process_breakdown', 'third_party', 'unknown']
SEVERITIES = ['error', 'warning']
RULES = [
    'sql-injection-001', 'hardcoded-secrets-002', 'eval-usage-003',
    'shell-injection-004', 'xxe-005', 'weak-crypto-006',
    'path-traversal-007', 'cors-wildcard-008', 'debug-enabled-009',
    'n1-query-010'
]

NOW = datetime.now(UTC)


async def seed_test_data(count: int = 200) -> dict[str, int]:
    """Seed test data covering 52-week period with varied attributes.

    Returns dict with counts: incidents, postmortems, by_team, by_category, by_severity.
    """
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError('DATABASE_URL environment variable required')

    # Convert psycopg2 URL to asyncpg URL
    if db_url.startswith('postgresql+psycopg2://'):
        db_url = db_url.replace('postgresql+psycopg2://', 'postgresql+asyncpg://')
    elif db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')

    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            print(f'Seeding {count} test incidents...')

            incidents_created = 0
            postmortems_created = 0
            stats = {team: 0 for team in TEAMS}
            cat_stats = {cat: 0 for cat in CATEGORIES}
            sev_stats = {sev: 0 for sev in SEVERITIES}

            for i in range(count):
                # Distribute across 52 weeks (oldest first)
                weeks_ago = (i % 52)
                created_at = NOW - timedelta(weeks=weeks_ago, days=i // 52)

                team = TEAMS[i % len(TEAMS)]
                category = CATEGORIES[i % len(CATEGORIES)]
                severity = SEVERITIES[i % len(SEVERITIES)]
                rule_id = RULES[i % len(RULES)]

                # ~30% resolved, ~70% unresolved
                resolved_at = created_at + timedelta(days=3) if i % 10 < 3 else None

                # Create incident
                incident = IncidentRow(
                    id=uuid4(),
                    title=f'Test Incident {i+1}: {category} in {team}',
                    category='injection',
                    severity='high',
                    anti_pattern=f'Pattern: {category} issue detected',
                    remediation=f'Fix the {category} vulnerability',
                    created_by=uuid4(),
                    resolved_at=resolved_at,
                    deleted_at=None,
                )
                session.add(incident)
                await session.flush()

                # Create postmortem
                postmortem = PostmortumRow(
                    id=uuid4(),
                    incident_id=incident.id,
                    root_cause_category=category,
                    description=f'Root cause analysis for {category}: {team} team incident',
                    team_responsible=team,
                    severity_for_rule=severity,
                    related_rule_id=rule_id,
                    created_by=uuid4(),
                    created_at=created_at,
                )
                session.add(postmortem)
                await session.flush()

                incidents_created += 1
                postmortems_created += 1
                stats[team] += 1
                cat_stats[category] += 1
                sev_stats[severity] += 1

                if (i + 1) % 50 == 0:
                    print(f'  {i + 1}/{count} created...')

            await session.commit()
            print(f'\n✅ Seeded {incidents_created} incidents + {postmortems_created} postmortems\n')

            # Print distribution
            print('Distribution by team:')
            for team, cnt in sorted(stats.items(), key=lambda x: -x[1]):
                print(f'  {team}: {cnt}')

            print('\nDistribution by category:')
            for cat, cnt in sorted(cat_stats.items(), key=lambda x: -x[1]):
                print(f'  {cat}: {cnt}')

            print('\nDistribution by severity:')
            for sev, cnt in sorted(sev_stats.items(), key=lambda x: -x[1]):
                print(f'  {sev}: {cnt}')

            print(f'\nTimeline: {NOW - timedelta(weeks=51)} to {NOW}')
            print('\n📌 To delete all test data later:')
            print("""
  DELETE FROM postmortems WHERE created_by IN (
    SELECT id FROM incidents WHERE title LIKE 'Test Incident%'
  );
  DELETE FROM incidents WHERE title LIKE 'Test Incident%';
            """)

            return {
                'incidents': incidents_created,
                'postmortems': postmortems_created,
                'by_team': stats,
                'by_category': cat_stats,
                'by_severity': sev_stats,
            }

    finally:
        await engine.dispose()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, default=200, help='Number of incidents to seed')
    args = parser.parse_args()

    import asyncio
    result = asyncio.run(seed_test_data(args.count))
