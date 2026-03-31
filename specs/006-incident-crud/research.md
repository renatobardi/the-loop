# Research: Incident Module — CRUD (Phase A)

**Branch**: `006-incident-crud` | **Date**: 2026-03-31

## 1. Monorepo Structure: Adding a Python Backend

**Decision**: Add `apps/api/` alongside existing `apps/web/` in the monorepo.

**Rationale**: The existing monorepo pattern (`apps/web/`) already supports multiple apps. A separate `apps/api/` directory keeps Python and Node.js codebases isolated with independent dependency management, Docker builds, and CI pipelines, while sharing specs and documentation at the repo root.

**Alternatives considered**:
- Separate repository: Rejected — increases coordination overhead, splits specs from implementation, complicates shared CI/docs gates.
- Backend inside `apps/web/` (API routes in SvelteKit): Rejected — SvelteKit server routes are Node.js-based; the spec mandates FastAPI + SQLAlchemy + Pydantic, and hexagonal architecture requires a proper Python domain layer.

## 2. FastAPI + SQLAlchemy Async Setup

**Decision**: FastAPI with SQLAlchemy 2.0 async (using asyncpg driver) and Pydantic v2 models for the domain layer.

**Rationale**: SQLAlchemy 2.0's native async support via `AsyncSession` integrates cleanly with FastAPI's async endpoints. asyncpg is the highest-performance PostgreSQL driver for Python async. Pydantic v2 is the standard for FastAPI request/response validation and aligns with the predecessor's frozen model pattern.

**Key patterns**:
- `AsyncSession` via `async_sessionmaker` with dependency injection
- Repository adapter receives session, not engine — testable via in-memory SQLite or test transaction rollback
- Domain models are pure Pydantic (frozen=True), separate from SQLAlchemy ORM models
- Mapping layer converts between ORM ↔ domain at the adapter boundary

**Alternatives considered**:
- Tortoise ORM: Rejected — smaller ecosystem, less mature async support compared to SQLAlchemy 2.0.
- Raw asyncpg without ORM: Rejected — loses migration support (Alembic), more boilerplate for complex queries.

## 3. Hexagonal Architecture Layout

**Decision**: Three-layer structure within `apps/api/src/`: `domain/` (pure Python), `ports/` (Protocol classes), `adapters/` (SQLAlchemy, FastAPI routes).

**Rationale**: Mandamento X requires hexagonal architecture from Phase 1. The domain layer has zero external dependencies — only Pydantic (which is pure validation, not infrastructure). Ports use Python's `Protocol` for structural subtyping (no abstract base classes needed). Only one port exists in Phase A: `IncidentRepoPort`.

**Boundary justification**: The PostgreSQL adapter is a real boundary — it can be swapped for test doubles, and the domain logic (validation, optimistic locking checks, soft-delete rules) must be testable without a database.

**Alternatives considered**:
- No port for Phase A (direct DB access): Rejected — violates Mandamento X, and the predecessor validated that this port enables isolated domain testing.
- Multiple ports (EmbeddingPort, VectorSearchPort): Rejected — speculative interfaces; these don't exist in Phase A per spec.

## 4. Firebase Auth Integration with FastAPI

**Decision**: Firebase Admin SDK verifies session cookies in a FastAPI dependency. Middleware extracts and validates the Firebase ID token from the `Authorization: Bearer <token>` header or session cookie.

**Rationale**: The existing `apps/web/` already uses Firebase for waitlist auth context. Reusing Firebase Auth maintains consistency. The FastAPI dependency pattern (`Depends(get_current_user)`) injects the authenticated user ID into route handlers, which flows to `created_by` on incident creation.

**Key patterns**:
- `firebase-admin` SDK initialized once at app startup (singleton, same pattern as `apps/web/src/lib/server/firebase.ts`)
- Auth dependency returns user UID (UUID) — no role checks in Phase A (FR-020)
- Rate limiting keyed by user UID, not IP (FR-022: 60 req/min per user)

**Alternatives considered**:
- Custom JWT verification without Firebase SDK: Rejected — duplicates Firebase validation logic, higher maintenance burden.
- API key-based auth: Rejected — weaker security model, doesn't integrate with Firebase user management.

## 5. Database Migrations with Alembic

**Decision**: Alembic with async support for schema migrations, initialized in `apps/api/`.

**Rationale**: Alembic is the standard migration tool for SQLAlchemy. Async Alembic runner works with the asyncpg engine. Initial migration creates the `incidents` table with pgvector extension enabled (but no HNSW index until Phase C).

**Key patterns**:
- `alembic/` directory at `apps/api/alembic/`
- `env.py` configured for async with `run_async_migrations()`
- Migration naming: `001_create_incidents_table.py`
- pgvector extension created via `CREATE EXTENSION IF NOT EXISTS vector` in first migration

## 6. Frontend-Backend Integration

**Decision**: SvelteKit frontend calls FastAPI backend via REST API. In development, Vite proxy forwards `/api/*` requests to FastAPI at `localhost:8000`. In production, both services run as separate Cloud Run instances with the frontend calling the API via internal URL.

**Rationale**: Separating frontend and backend as distinct Cloud Run services follows the existing single-service deployment pattern (just adding a second service). The Vite dev proxy provides seamless DX without CORS complexity during development.

**Alternatives considered**:
- Single Cloud Run instance running both: Rejected — couples deployment, complicates scaling, mixes Node.js and Python runtimes.
- SvelteKit server-side proxy in production: Rejected — adds latency hop, makes SvelteKit a bottleneck for API traffic.

## 7. CI/CD for Multi-Service

**Decision**: Extend existing CI workflow with a parallel `api-quality` job. Add a separate deploy job for the API service.

**Rationale**: The existing CI (`ci.yml`) runs quality/security/docs jobs for `apps/web/`. Adding a parallel `api-quality` job (ruff, mypy, pytest, Docker build, Trivy) keeps both services gated independently. Deploy workflow gets a second Cloud Run deploy step for `apps/api/`.

**Key patterns**:
- CI: `web-quality` + `api-quality` jobs run in parallel
- API quality gates: ruff (lint), mypy strict (type-check), pytest with coverage (test), Docker build, Trivy scan
- Deploy: two sequential Cloud Run deploys (web then API, or parallel)
- Path filters: API CI only triggers on `apps/api/**` changes (optimization)

## 8. Rate Limiting Strategy

**Decision**: `slowapi` (FastAPI-native rate limiting built on `limits` library) with in-memory storage for Phase A, keyed by authenticated user UID.

**Rationale**: slowapi integrates natively with FastAPI's dependency injection and provides decorator-based rate limiting. In-memory storage is sufficient for a single Cloud Run instance in Phase A. If horizontal scaling is needed later, swap to Redis backend.

**Alternatives considered**:
- rate-limiter-flexible (used in apps/web/): Rejected — Node.js library, not available in Python.
- Custom middleware: Rejected — reinvents what slowapi already provides.
- Redis-backed from day 1: Rejected — adds infrastructure complexity without Phase A need (single instance).

## 9. Testing Strategy

**Decision**: pytest with async support (pytest-asyncio), three layers: unit (domain), integration (repository adapter with test DB), API (FastAPI TestClient).

**Rationale**: Aligns with Mandamento VII (CI gates: test) and Mandamento IX (tests as documentation). The hexagonal architecture enables pure domain unit tests without DB. Integration tests use a real PostgreSQL test database (not mocks — lesson from predecessor). API tests use FastAPI's TestClient for end-to-end route testing.

**Key patterns**:
- `tests/unit/` — domain logic (validation, optimistic locking, soft-delete rules)
- `tests/integration/` — repository adapter with test PostgreSQL (Docker in CI)
- `tests/api/` — FastAPI TestClient with test DB
- Fixtures: `conftest.py` with async session factory, test DB creation/teardown
- Coverage target: to be defined per phase (Mandamento VII)

## 10. Observability (Deferred from Clarification)

**Decision**: Structured JSON logging via `structlog` for Phase A. Metrics and tracing deferred to a future phase.

**Rationale**: Mandamento VIII (Camada 4) requires audit logging. structlog provides structured, JSON-formatted logs that integrate with Cloud Run's Cloud Logging. This gives basic observability without adding metrics/tracing infrastructure complexity in Phase A.

**Key patterns**:
- Request ID middleware (UUID per request, included in all log entries)
- Log levels: INFO for CRUD operations, WARNING for rate limits, ERROR for unhandled exceptions
- No APM/tracing in Phase A — revisit when traffic warrants it
