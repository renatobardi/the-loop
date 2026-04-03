# Spec-011 Phase B — API Integration + Versionamento

**Status**: Specification Phase (Completed) → Implementation Phase (Starting)  
**Branch**: `feat/phase-b-api-integration`  
**Timeline**: 3-4 weeks (part-time) or 4-5 days (full-time sprint)  
**Updated**: 2026-04-03

---

## Phase B Overview

Phase B moves rules distribution from static files (Phase A) to a versioned API. This enables:
- **Semantic versioning** (0.1.0, 0.2.0, ...) with rollback support
- **Live rule updates** without redeploying projects using The Loop
- **Deprecation lifecycle** (DRAFT → ACTIVE → DEPRECATED)
- **Admin publish control** via Firebase auth
- **Workflow fallback** if API is unavailable (uses Phase A .yml as backup)

---

## Architectural Decisions

### 1. **API Versioning Strategy**

**Decision**: Endpoint versioning via `/api/v1/` prefix, semantic versioning for rule sets.

**Rationale**:
- `/api/v1/` provides forward compatibility (if /v2 needed in future, both can coexist)
- Semantic versioning (semver) matches npm/pip ecosystem expectations — familiar to users
- Server-side storage in PostgreSQL `rule_versions` table enables rollback without code deploy

**Constraints**:
- No major version changes planned for Phase B/C (v0.2.0 max)
- Deprecated versions remain queryable for audit/rollback purposes

---

### 2. **Caching Strategy**

**Decision**: In-memory TTL cache (300 seconds = 5 minutes) for `/latest` endpoint, no Redis dependency.

**Rationale**:
- Reduces database queries by ~95% (5-min refresh cycle)
- No external dependency (Redis) needed for MVP
- Simple Python dict with expiry timestamp
- Phase C can upgrade to Redis if needed

**Invalidation**:
- Manual on POST /publish (immediate)
- Automatic expiry after 5 minutes
- `rules:latest` key only (other versions not cached)

**Performance Target**: <10ms cached, <100ms uncached (DB query)

---

### 3. **Workflow Integration & Fallback**

**Decision**: GitHub Actions workflow fetches from API with 5-second timeout; falls back to `.semgrep/theloop-rules.yml.bak` if API unavailable.

**Rationale**:
- No breaking change to Phase A workflows — they continue working
- Fallback ensures CI/CD resilience if API down
- 5-second timeout prevents PR feedback delay (normal API response <100ms)
- json_to_semgrep_yaml.py conversion script adds flexibility

**Fallback Trigger**: API timeout OR HTTP 503/500 errors → use local .bak file

---

### 4. **Database Schema Design**

**Decision**: Single `rule_versions` table with JSONB `rules_json` column + constraints.

**Rationale**:
- JSONB allows flexible rule structure (can evolve without migration)
- Constraints enforce semver format (`^[0-9]+\.[0-9]+\.[0-9]+$`) and deprecation logic
- Three indexes on `status`, `version`, `created_at` for fast queries
- Soft delete via `deprecated_at` timestamp

**Constraints**:
- `version` UNIQUE — no duplicate versions
- `status` CHECK — only DRAFT, ACTIVE, DEPRECATED
- `valid_deprecation` CHECK — if deprecated, must have deprecated_at timestamp

---

### 5. **Authentication & Authorization**

**Decision**: Firebase token verification + admin role check (claims.admin == True) for POST /publish.

**Rationale**:
- Leverages existing Firebase integration (Phase 1 auth)
- Admin role currently manual claim (future: Firestore custom claims or dedicated admin_users table)
- GET endpoints public (no auth required) — rules are open

**Future Evolution**: Move admin check to Firestore custom claims or dedicated table if needed

---

### 6. **Rate Limiting**

**Decision**: slowapi library (existing dependency) with 60/min for GETs, 10/min for POSTs.

**Rationale**:
- Already in Phase 1 API codebase
- Conservative limits prevent abuse without impacting normal workflows
- GET-heavy (read) vs POST-rare (publish) reflects expected access pattern

---

## Specification Artifacts

### tasks.md Structure

**74 tasks** organized in 6 phases:

1. **Phase 1: Setup & Infrastructure (T001-T010)**
   - Directory structure, dev dependencies, pre-commit hooks
   - Alembic migration scaffold + local test
   - Seed v0.1.0 (6 Phase A rules)

2. **Phase 2: Database & Domain Layer (T011-T025)**
   - ORM models (RuleVersionRow, SQLAlchemy)
   - Domain models (Rule, RuleVersion, RuleVersionStatus enums)
   - Exceptions (RuleVersionNotFoundError, VersionAlreadyExistsError, etc.)
   - Repository pattern (protocol + PostgreSQL adapter)
   - Unit tests (Pydantic validation, semver format)

3. **Phase 3: Service Layer & API Preparation (T026-T035)**
   - RuleVersionService (orchestrator)
   - RuleVersionCache (in-memory TTL)
   - Request/response models (PublishRulesRequest, RuleVersionResponse)
   - Authentication check (require_admin)
   - Rate limiting config

4. **Phase 4: API Endpoints (T036-T050)**
   - GET /api/v1/rules/latest (cached)
   - GET /api/v1/rules/{version} (any status)
   - GET /api/v1/rules/versions (list all)
   - POST /api/v1/rules/publish (admin)
   - Manual testing (curl), cache hit validation, error handling

5. **Phase 5: Workflow Integration & New Rules (T051-T074)**
   - Update .github/workflows/theloop-guard.yml (fetch from API)
   - scripts/json_to_semgrep_yaml.py conversion script
   - Create 14 new rules (injection, crypto, security, performance, infrastructure, config, dependencies)
   - Publish v0.2.0 (20 total rules)
   - Test fallback logic

6. **Phase 6: Testing & Documentation (T075-T098)**
   - Integration tests (Alembic on Cloud SQL, workflow E2E, rollback scenario)
   - Code coverage (≥80%), lint, type checking
   - API documentation, versioning guide, troubleshooting
   - PR review, merge, deploy verification

---

## Parallelization Opportunities

- **Week 1**: T003, T005, T009 (deps, hooks, config) can run in parallel
- **Week 2**: T011-T015 (ORM + exceptions), T019-T021 (unit tests) parallelizable
- **Week 3**: T036-T039 (endpoints), T058-T070 (rules) parallelizable
- **Week 4**: T075-T083 (integration tests, coverage, lint) parallelizable

---

## Key Dependencies

### Infrastructure
- **Database**: PostgreSQL 16 + pgvector extension (Cloud SQL)
- **Migrations**: Alembic v1.12+ (already in Phase 1)
- **Cache**: Python built-in (dict) with datetime for TTL
- **API**: FastAPI, SQLAlchemy 2.0 async, Pydantic v2 (all Phase 1)

### Libraries
- **asyncpg**: Async PostgreSQL driver (in requirements.txt)
- **sqlalchemy[asyncio]**: 2.0+ (in requirements.txt)
- **pydantic**: v2 (in requirements.txt)
- **slowapi**: Rate limiting (in requirements.txt)

### External Services
- **Firebase Admin SDK**: Token verification (in Phase 1)
- **Cloud SQL Proxy**: Local dev database (tunnel via `cloud_sql_proxy`)

### Deployment
- **Cloud Run**: Auto-deploy on push to main (existing CI/CD)
- **GitHub Actions**: Workflow fetch integration (new in Phase B)

---

## Risk Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| API break during rollout | MEDIUM | HIGH | Workflow fallback to Phase A rules |
| Bad rule published | MEDIUM | MEDIUM | Code review before publish; deprecate fast |
| DB migration fails | LOW | HIGH | Test locally first; dry-run migrations |
| Cache invalidation bug | LOW | MEDIUM | Unit tests for cache; monitor hits |
| Semver parsing error | LOW | LOW | Regex validation; tests for edge cases |

---

## Success Criteria (per Task Completion)

Each task MUST satisfy:
- ✅ Code written (if applicable)
- ✅ Tests added (unit or integration)
- ✅ Documentation updated
- ✅ No lint/type errors
- ✅ Commit message references task ID (e.g., "Closes T036")

---

## Checkpoint Validations

**After T010 (Setup)**: Alembic migration 007 created, v0.1.0 seeded, dev environment ready.

**After T025 (Domain)**: RuleVersion model validated, repository tests pass (mocked + integration), coverage ≥80%.

**After T050 (API)**: All 4 endpoints working, cache tested (<10ms hits), error handling comprehensive.

**After T074 (Workflow)**: v0.2.0 published (20 rules), workflow fetches from API, fallback tested.

**After T098 (Complete)**: All CI gates pass (lint, type, coverage ≥80%, security), PR merged, deployed to prod.

---

## Next Steps (Immediate)

1. **T001-T010**: Setup phase (dependencies, migrations, seed data) — this week
2. **Validate**: Local Alembic migration works, v0.1.0 seeds successfully
3. **T011-T025**: Domain layer (ORM + models + exceptions + repository) — parallel work
4. **T026-T035**: Service layer + API prep — depends on T025
5. **T036-T050**: API endpoints — depends on T035
6. **Validate**: All endpoints respond correctly, caching works
7. **T051-T074**: Workflow integration + new rules — depends on T050
8. **T075-T098**: Testing, docs, polish, merge

---

## How to Execute

```bash
cd /Users/bardi/Projetos/the-loop
git checkout feat/phase-b-api-integration

# Phase 1: Setup
T001-T010 (this session)

# Validate Phase 1
pytest tests/integration/test_db_constraints.py -v

# Phase 2: Domain layer
T011-T035 (parallel where marked [P])

# Phase 3: API endpoints
T036-T074 (parallel where marked [P])

# Phase 4: Finalize
T075-T098 (parallel where marked [P])

# Merge to main
git push -u origin feat/phase-b-api-integration
# Open PR, review, merge
```

---

**Referências**: specs/011-phase-b-api-integration/spec.md, plan.md, tasks.md
