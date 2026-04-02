# Quickstart: Incident Data Model — Production-Ready Schema

**Feature**: 008-incident-data-model  
**Date**: 2026-04-01

---

## Prerequisites

- PostgreSQL 16 running with pgvector (see `CLAUDE.md` — Local PostgreSQL Setup)
- `DATABASE_URL` exported: `postgresql+asyncpg://theloop:theloop@localhost:5432/theloop`
- Migration `001` already applied (`alembic upgrade head` from a clean state)

---

## Apply All Migrations

```bash
cd apps/api
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5432/theloop"
alembic upgrade head
```

This runs migrations `001` through `006` in sequence.

## Run Backfill Script (existing data only)

If the database has pre-existing incidents with `date != NULL`, populate `started_at`:

```bash
cd apps/api
python scripts/backfill_started_at.py
```

The script is idempotent — safe to run multiple times.

---

## Verify the Schema

```bash
# Connect to the database
psql postgresql://theloop:theloop@localhost:5432/theloop

# Check new columns on incidents
\d incidents

# Check new tables
\dt incident_*
```

Expected new tables: `incident_timeline_events`, `incident_responders`, `incident_action_items`, `incident_attachments`

---

## Run the Test Suite

```bash
cd apps/api
pytest tests/
```

Migration tests verify schema correctness. Domain tests verify computed properties. API tests verify new endpoints.

---

## Try the New API

Start the dev server:

```bash
cd apps/api
uvicorn src.main:app --reload
```

Get a Firebase ID token for a test user, then:

```bash
# Create an incident with operational timestamps
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Queue depth exceeded threshold",
    "category": "resource-exhaustion",
    "severity": "high",
    "anti_pattern": "No alerting on queue depth",
    "remediation": "Add Datadog monitor with 5k threshold",
    "started_at": "2026-03-15T14:00:00Z",
    "detected_at": "2026-03-15T14:05:00Z",
    "ended_at": "2026-03-15T15:30:00Z"
  }'
# Response includes: duration_minutes: 90, time_to_detect_minutes: 5

# Add a timeline event
INCIDENT_ID="<id from above>"
curl -X POST http://localhost:8000/api/v1/incidents/$INCIDENT_ID/timeline \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "detected",
    "description": "Datadog alert fired",
    "occurred_at": "2026-03-15T14:05:00Z",
    "recorded_by": "<your-firebase-uid>"
  }'

# Create an action item
curl -X POST http://localhost:8000/api/v1/incidents/$INCIDENT_ID/action-items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lower queue depth alert threshold to 5k",
    "priority": "high",
    "due_date": "2026-04-01"
  }'
```

---

## Rollback a Migration

```bash
cd apps/api
alembic downgrade -1   # Roll back one step
alembic downgrade 001  # Roll back to initial schema
```
