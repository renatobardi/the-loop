# Plan-011: Phase B — API Integration + Versionamento

**Fase:** B  
**Duração:** 3-4 semanas (mai-jun)  
**Objetivo técnico:** Mover rules de arquivo estático para API versionsda

---

## Constitution Check

**Mandamentos aplicáveis:**

- **I. Trunk-based:** Feature branch `feat/phase-b-api-integration` → PR → merge main
- **II. Code review:** PR obrigatória, review por @renatobardi
- **IV. Hexagonal:** domain/models + ports/adapters pattern
- **VI. Type safety:** mypy strict, Pydantic v2
- **VII. Coverage:** ≥80% (pytest --cov)
- **IX. Security:** Prepared statements (SQLAlchemy), auth check (admin)
- **XIII. Dependencies:** ALL deps in tasks.md (DB schema, API auth, etc)

**Status:** ✅ Compliant

---

## Technical Context

### Stack

**Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 async  
**Database:** PostgreSQL 16 (Cloud SQL, async driver asyncpg)  
**Deployment:** Cloud Run (auto-deploy on merge)  
**Testing:** pytest (unit + integration), mocking for API tests  
**Caching:** In-memory (Python dict with TTL) — Redis optional Phase C

### Architecture Pattern

```
Domain Layer (pure Python):
  ├─ RuleVersion (Pydantic model)
  ├─ RuleVersionService (orchestrator)
  └─ RuleVersionNotFoundError, VersionAlreadyExistsError (typed exceptions)

Ports Layer (protocols):
  └─ RuleVersionRepository (CRUD interface)

Adapters Layer:
  ├─ PostgresRuleVersionRepository (ORM)
  ├─ RuleVersionRow (SQLAlchemy model)
  └─ Cache adapter (in-memory TTL)

API Layer:
  ├─ GET /api/v1/rules/latest
  ├─ GET /api/v1/rules/{version}
  ├─ GET /api/v1/rules/versions
  └─ POST /api/v1/rules/publish (admin)
```

---

## Data Model

### rule_versions Table

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

### Updated incidents Table

```sql
ALTER TABLE incidents ADD COLUMN rules_version_used VARCHAR(20);
-- Track which rule version was active when incident was found/fixed
```

### Domain Model (Pydantic)

```python
class RuleVersionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"

class Rule(BaseModel):
    id: str
    languages: List[str]
    message: str
    severity: Literal["ERROR", "WARNING"]
    metadata: Dict[str, Any]
    patterns: List[Dict[str, Any]]

class RuleVersion(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: UUID
    version: str  # "0.2.0"
    rules: List[Rule]
    status: RuleVersionStatus
    created_at: datetime
    published_by: UUID
    notes: Optional[str] = None
    deprecated_at: Optional[datetime] = None
    
    @field_validator('version')
    @classmethod
    def validate_semver(cls, v: str) -> str:
        if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+$', v):
            raise ValueError(f"Invalid semver: {v}")
        return v
    
    @property
    def rules_count(self) -> int:
        return len(self.rules)
```

---

## API Endpoints

### Endpoint 1: GET /api/v1/rules/latest

```
Request:
  GET /api/v1/rules/latest
  
Response 200:
  Content-Type: application/json
  Cache-Control: public, max-age=300
  
  {
    "version": "0.2.0",
    "rules_count": 20,
    "created_at": "2026-05-15T10:00:00Z",
    "status": "active",
    "rules": [
      {
        "id": "injection-001",
        "languages": ["python", "javascript", ...],
        "message": "[The Loop] SQL injection...",
        "severity": "ERROR",
        "metadata": {
          "incident_id": "injection-001",
          "category": "injection",
          "loop_url": "https://loop.oute.pro/incidents/injection-001"
        },
        "patterns": [...]
      },
      ...
    ]
  }

Response 503 (API error, fallback triggered):
  {
    "error": "ServiceUnavailable",
    "detail": "Rules service temporarily unavailable"
  }
```

**Implementation:**
```python
@router.get("/api/v1/rules/latest")
@limiter.limit("60/minute")
async def get_latest_rules(request: Request, service: RuleVersionService = Depends(get_rule_version_service)):
    rule_version = await service.get_latest_active()
    if not rule_version:
        raise RuleVersionNotFoundError("No active rule version found")
    return {
        "version": rule_version.version,
        "rules_count": rule_version.rules_count,
        "created_at": rule_version.created_at,
        "status": rule_version.status,
        "rules": rule_version.rules
    }
```

---

### Endpoint 2: GET /api/v1/rules/{version}

```
Request:
  GET /api/v1/rules/v0.1.0
  
Response 200:
  { "version": "0.1.0", "rules": [...] }  (mesmo formato que latest)

Response 404:
  {
    "error": "RuleVersionNotFound",
    "detail": "Version 0.1.0 not found"
  }
```

---

### Endpoint 3: GET /api/v1/rules/versions

```
Response 200:
  {
    "versions": [
      {
        "version": "0.1.0",
        "status": "deprecated",
        "created_at": "2026-04-03T16:00:00Z",
        "rules_count": 6,
        "deprecated_at": "2026-05-15T10:00:00Z"
      },
      {
        "version": "0.2.0",
        "status": "active",
        "created_at": "2026-05-15T10:00:00Z",
        "rules_count": 20,
        "deprecated_at": null
      }
    ]
  }
```

---

### Endpoint 4: POST /api/v1/rules/publish

```
Request:
  POST /api/v1/rules/publish
  Authorization: Bearer {admin_firebase_token}
  Content-Type: application/json
  
  {
    "version": "0.3.0",
    "rules": [
      {
        "id": "injection-001",
        "languages": ["python", "javascript", ...],
        "message": "...",
        "severity": "ERROR",
        "metadata": {...},
        "patterns": [...]
      },
      ...
    ],
    "notes": "Add 22-24 new rules, improve ReDoS detection"
  }

Response 201:
  {
    "message": "Published v0.3.0 with 22 rules",
    "version": "0.3.0",
    "created_at": "2026-05-20T14:00:00Z",
    "rules_count": 22
  }

Response 409 (version exists):
  {
    "error": "VersionAlreadyExists",
    "detail": "Version 0.3.0 already exists"
  }

Response 403 (unauthorized):
  {
    "error": "Unauthorized",
    "detail": "Admin role required"
  }
```

**Implementation:**
```python
@router.post("/api/v1/rules/publish")
@limiter.limit("10/minute")
async def publish_rules(
    request: Request,
    body: PublishRulesRequest,
    user: User = Depends(require_auth),
    service: RuleVersionService = Depends(get_rule_version_service)
):
    # Check admin
    if not user.is_admin:
        raise UnauthorizedError("Admin role required")
    
    # Create RuleVersion
    new_version = await service.publish_version(
        version=body.version,
        rules=body.rules,
        published_by=user.id,
        notes=body.notes
    )
    
    # Invalidate cache
    await cache.invalidate("rules:latest")
    
    return {
        "message": f"Published {new_version.version} with {new_version.rules_count} rules",
        "version": new_version.version,
        "created_at": new_version.created_at,
        "rules_count": new_version.rules_count
    }
```

---

## Caching Strategy

### Cache Key: `rules:latest`

```python
class RuleVersionCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl_seconds = ttl_seconds
    
    async def get_latest(self) -> Optional[RuleVersion]:
        key = "rules:latest"
        if key in self.cache:
            cached, expires_at = self.cache[key]
            if datetime.now() < expires_at:
                return cached
            else:
                del self.cache[key]
        return None
    
    async def set_latest(self, rule_version: RuleVersion):
        key = "rules:latest"
        expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)
        self.cache[key] = (rule_version, expires_at)
    
    async def invalidate(self):
        self.cache.pop("rules:latest", None)
```

**Cache hits:** ~95% of requests (5 min TTL)  
**Cache misses:** <100ms (DB query)  
**Invalidation:** On POST /publish (instant)

---

## Workflow Integration (Phase A → Phase B)

### Before (Phase A)
```yaml
# .github/workflows/theloop-guard.yml
- name: Run Semgrep scan
  run: |
    semgrep scan \
      --config .semgrep/theloop-rules.yml \
      --json --output results.json
```

### After (Phase B)

```yaml
- name: Fetch latest rules from API
  run: |
    curl -s \
      --max-time 5 \
      https://theloop-api.run.app/api/v1/rules/latest \
      -o rules-api.json || {
        echo "API unavailable, using cached rules"
        cp .semgrep/theloop-rules.yml.bak rules-api.json
      }

- name: Convert JSON to YAML
  run: python3 scripts/json_to_semgrep_yaml.py rules-api.json

- name: Run Semgrep scan
  run: |
    semgrep scan \
      --config .semgrep/theloop-rules.yml \
      --json --output results.json
```

**Fallback:** Se API timeout (>5s), usa `.semgrep/theloop-rules.yml` (backup local)

---

## Authentication & Authorization

### Admin Check

```python
async def require_admin(user: User = Depends(require_auth)) -> User:
    # Verify Firebase token
    try:
        claims = firebase_admin.auth.verify_id_token(token)
    except:
        raise UnauthorizedError("Invalid token")
    
    # Check admin role (future: Firestore custom claims)
    if claims.get("admin") != True:
        raise UnauthorizedError("Admin role required")
    
    return user
```

**Current:** Manual check (claims.admin)  
**Future:** Firestore custom claims or Postgres admin_users table

---

## File Structure

```
apps/api/src/
  adapters/postgres/
    models.py
      └─ RuleVersionRow (new)
    
    rule_version_repository.py (new)
      └─ PostgresRuleVersionRepository
    
    cache.py
      └─ RuleVersionCache (new)
  
  domain/
    models.py
      ├─ RuleVersion (new)
      ├─ RuleVersionStatus (new)
      └─ Rule (new)
    
    exceptions.py
      ├─ RuleVersionNotFoundError (new)
      ├─ VersionAlreadyExistsError (new)
      ├─ InvalidVersionFormatError (new)
      └─ UnauthorizedPublishError (new)
    
    services.py
      └─ RuleVersionService (new)
  
  ports/
    rule_version_repo.py (new)
      └─ RuleVersionRepository (protocol)
  
  api/
    routes/
      rules.py (new)
        ├─ GET /api/v1/rules/latest
        ├─ GET /api/v1/rules/{version}
        ├─ GET /api/v1/rules/versions
        └─ POST /api/v1/rules/publish
    
    deps.py (updated)
      ├─ get_rule_version_repository
      ├─ get_rule_version_service
      └─ get_rule_version_cache

alembic/versions/
  007_create_rule_versions.py (new)

tests/
  unit/
    domain/
      test_rule_version.py (new)
      test_rule_version_service.py (new)
  
  api/
    test_rules.py (new)
  
  integration/
    test_rule_versions_integration.py (new)

scripts/
  json_to_semgrep_yaml.py (new)
    └─ Convert API JSON → Semgrep YAML

specs/011/
  spec.md (this file)
  plan.md
  tasks.md
  data-model.md
```

---

## Testing Strategy

### Unit Tests (no DB)

**test_rule_version.py:**
- Pydantic validation (semver format, frozen)
- Rules count property
- Status enum

**test_rule_version_service.py:**
- get_latest_active() returns latest with status="active"
- get_by_version() returns specific version (any status)
- publish_version() creates new version, invalidates cache
- publish_version() rejects duplicate version

### Integration Tests (with DB)

**test_rule_versions_integration.py:**
- Alembic migration 007 applies cleanly
- Seed v0.1.0 (6 rules) works
- Query by version returns correct rules
- Deprecation logic works

### API Tests (mocked services)

**test_rules.py:**
- GET /latest returns v0.2.0 (latest)
- GET /latest is cached (<10ms second call)
- GET /v0.1.0 works (deprecated)
- GET /v999.0.0 returns 404
- POST /publish requires admin (403 if not)
- POST /publish rejects invalid semver (400)
- POST /publish returns 201 with rules_count=20

### End-to-End (workflow simulation)

- Fetch API → convert JSON → scan → same behavior as Phase A

---

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|---|
| API latency (cached) | <10ms | `time curl /latest` (repeat) |
| API latency (uncached) | <100ms | `time curl /latest` (cold start) |
| Cache hit rate | ≥95% | CloudRun metrics |
| Fallback activation | <5s | Workflow logs (if API down) |
| Migration time | <1 min | `alembic upgrade head` timing |
| Database query | <50ms | CloudSQL metrics |

---

## Rollout Plan

### Week 1: Infrastructure
- Create rule_versions table + migration
- Seed v0.1.0 (copy current Phase A rules)
- Create domain model + repository
- Unit tests (coverage ≥80%)

### Week 2: API
- Create 4 endpoints (GET latest, GET version, GET versions, POST publish)
- Add caching + rate limiting
- API tests (coverage ≥80%)
- Publish v0.2.0 (6 original + 14 new = 20 rules)

### Week 3: Workflow Integration
- Update .github/workflows/theloop-guard.yml
- Add fallback logic
- Test workflow integration
- Document Phase B for users

### Week 4: Polish
- Final testing (integration + E2E)
- Documentation complete
- Code review + merge
- Deploy to production

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| API break during rollout | MEDIUM | HIGH | Workflow fallback to Phase A rules |
| Bad rule published | MEDIUM | MEDIUM | Code review before publish; deprecate fast |
| DB migration fails | LOW | HIGH | Test locally first; dry-run migrations |
| Cache invalidation bug | LOW | MEDIUM | Unit tests for cache; monitor hits |
| Semver parsing error | LOW | LOW | Regex validation; tests for edge cases |

---

**Última atualização:** 2026-04-03  
**Próxima revisão:** Kickoff meeting (antes de T001)
