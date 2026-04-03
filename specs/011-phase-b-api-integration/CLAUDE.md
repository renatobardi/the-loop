# Phase B — Tech Decisions & Implementation Guide

This document records key technical decisions for Phase B API integration implementation.

## Architecture

### Hexagonal Pattern (domain/ports/adapters)

All new code follows the hexagonal pattern:

1. **Domain Layer** (`domain/models.py`, `domain/services.py`, `domain/exceptions.py`)
   - Pure Python: `Rule`, `RuleVersion`, `RuleVersionStatus` (Pydantic frozen models)
   - Typed exceptions: `RuleVersionNotFoundError`, `VersionAlreadyExistsError`, `InvalidVersionFormatError`
   - Service: `RuleVersionService` (orchestrator, raises domain exceptions never HTTP)

2. **Ports Layer** (`ports/rule_version_repo.py`)
   - Protocol: `RuleVersionRepository` with abstract methods
   - Methods: `get_latest_active()`, `get_by_version()`, `list_all()`, `publish_version()`, `deprecate_version()`

3. **Adapters Layer**
   - **ORM**: `adapters/postgres/models.py` → `RuleVersionRow` (SQLAlchemy with `Mapped[T]`)
   - **Repository**: `adapters/postgres/rule_version_repository.py` → `PostgresRuleVersionRepository` (implements protocol)
   - **Cache**: `adapters/postgres/cache.py` → `RuleVersionCache` (in-memory TTL)

4. **API Layer** (`api/routes/rules.py`)
   - Request/response models: `PublishRulesRequest`, `RuleVersionResponse`
   - Handlers: GET/POST endpoints with rate limiting + auth checks
   - Dependency injection: `Depends(get_rule_version_service)`

### SQLAlchemy 2.0 Async

All database operations use async/await:

```python
async def get_by_version(self, version: str) -> Optional[RuleVersion]:
    stmt = select(RuleVersionRow).where(RuleVersionRow.version == version)
    result = await self.session.execute(stmt)
    row = result.scalars().first()
    return self._row_to_domain(row) if row else None
```

Enum handling:
- Store `.value` in database (string)
- Reconstruct via `RuleVersionStatus(row.status)` in `_row_to_domain()`

### Caching Strategy

**In-Memory TTL Cache**:
```python
class RuleVersionCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}  # {"rules:latest": (RuleVersion, expires_at)}
        self.ttl_seconds = ttl_seconds
    
    async def get_latest(self) -> Optional[RuleVersion]:
        key = "rules:latest"
        if key in self.cache:
            cached, expires_at = self.cache[key]
            if datetime.now() < expires_at:
                return cached
        return None
    
    async def invalidate(self):
        self.cache.pop("rules:latest", None)
```

**Key points**:
- Single key: `rules:latest`
- TTL: 300 seconds (5 minutes)
- Invalidated on POST /publish (immediate)
- Phase C can upgrade to Redis

### Authentication & Authorization

**Firebase Admin Check**:
```python
async def require_admin(user: User = Depends(require_auth)) -> User:
    # user.is_admin must be True (from Firebase claims)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin role required")
    return user
```

Future: Move `is_admin` to Firestore custom claims or dedicated `admin_users` table.

## Database

### Migration Strategy

Alembic revision 007 creates `rule_versions` table:

```sql
CREATE TABLE rule_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  version VARCHAR(20) NOT NULL UNIQUE,
  rules_json JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  published_by UUID NOT NULL,
  notes TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'draft',
    CONSTRAINT status_check CHECK (status IN ('draft', 'active', 'deprecated')),
  deprecated_at TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT version_format CHECK (version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'),
  CONSTRAINT valid_deprecation CHECK (
    (status = 'deprecated' AND deprecated_at IS NOT NULL) OR
    (status != 'deprecated' AND deprecated_at IS NULL)
  )
);

CREATE INDEX idx_rule_versions_status ON rule_versions(status);
CREATE INDEX idx_rule_versions_version ON rule_versions(version);
CREATE INDEX idx_rule_versions_created_at ON rule_versions(created_at DESC);
```

**Constraints**:
- `version` UNIQUE — no duplicate versions
- Semver validation via regex CHECK
- `deprecated_at` required if status='deprecated'

### Seed Data

v0.1.0 initial rules (from Phase A):
- injection-001, injection-002, unsafe-api-usage-001, missing-safety-check-001, missing-error-handling-001, unsafe-regex-001

Seeded as single JSONB entry in `rule_versions` table with status='active'.

## API Endpoints

### GET /api/v1/rules/latest
- Public (no auth)
- Rate limit: 60/min
- Cache: 5-min TTL
- Returns: `RuleVersionResponse` with full rules array

### GET /api/v1/rules/{version}
- Public (no auth)
- Rate limit: 60/min
- No cache (specific version query)
- Returns: `RuleVersionResponse` or 404

### GET /api/v1/rules/versions
- Public (no auth)
- Rate limit: 60/min
- Returns: `{"versions": [{"version": "0.1.0", "status": "active", ...}]}`

### POST /api/v1/rules/publish
- Requires admin auth
- Rate limit: 10/min
- Expects: `PublishRulesRequest` (version, rules array, notes)
- Returns: 201 with `{"message": "...", "version": "...", "rules_count": N}`
- Side effect: Invalidates `/latest` cache

## Testing

### Unit Tests (no DB)

`tests/unit/domain/test_rule_version.py`:
- Pydantic validation (frozen, semver format)
- Rules count property
- Status enum

### Integration Tests (with DB)

`tests/integration/test_rule_versions_integration.py`:
- Alembic migration 007 applies cleanly
- Seed v0.1.0 works
- Query by version returns correct rules
- Deprecation logic works

### API Tests (mocked services)

`tests/api/test_rules.py`:
- GET /latest returns v0.2.0
- Cache hit (<10ms second request)
- GET /v0.1.0 works (deprecated)
- GET /v999.0.0 returns 404
- POST /publish requires admin (403 if not)
- POST /publish rejects invalid semver (400)

## Code Style

- **Type hints**: All function signatures must have return types
- **Async**: All DB operations use `async def` + `await`
- **Frozen models**: `ConfigDict(frozen=True)` on all Pydantic models
- **No imports from `__future__`** (conflicts with slowapi)
- **Enums**: Use `StrEnum` from domain/models.py
- **Exceptions**: Typed, domain-level (no HTTP status codes in domain)

## Common Patterns

### Repository `_row_to_domain()` Helper

```python
def _row_to_domain(self, row: RuleVersionRow) -> RuleVersion:
    return RuleVersion(
        id=row.id,
        version=row.version,
        rules=[...],  # Parse from row.rules_json
        status=RuleVersionStatus(row.status),
        created_at=row.created_at,
        published_by=row.published_by,
        notes=row.notes,
        deprecated_at=row.deprecated_at,
    )
```

### Route `_get_parent_or_404()` Helper

For sub-resources, always validate parent:
```python
async def _get_rule_version_or_404(version: str, service: RuleVersionService):
    rv = await service.get_by_version(version)
    if not rv:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    return rv
```

## Troubleshooting

### `asyncpg.exceptions.UndefinedTableError`
Migration 007 not applied. Run: `alembic upgrade head`

### `RuleVersionNotFoundError` (service) vs 404 (API)
Domain exceptions are raised by service, caught + converted to HTTP status by route handler.

### Cache hit not working
- Check TTL: `datetime.now() < expires_at`
- Check invalidation: POST /publish calls `await cache.invalidate()`
- Monitor `self.cache` contents in debug

### Enum value error
If `status='DRAFT'` but code expects `RuleVersionStatus.DRAFT`, check database values are lowercase: `'draft'`, `'active'`, `'deprecated'`.

---

**Reference**: specs/011-phase-b-api-integration/plan.md (detailed architecture)
