# Spec-012: Phase B — Workflow Integration + 14 New Rules

**Status**: Planning → Implementation  
**Branch**: `feat/phase-b-workflow-integration`  
**Fase**: B (Continuation) — Workflow & Rule Expansion  
**Timeline**: 8-11 dias

---

## Objetivo

Integrar Phase B API (rule versioning) ao GitHub Actions workflow e expandir regra base de 6 para 20 regras Semgrep.

**Deliverables**:
1. Updated `.github/workflows/theloop-guard.yml` — fetch rules from API + fallback
2. `scripts/json_to_semgrep_yaml.py` — JSON → YAML conversion utility
3. 14 novas regras Semgrep (categories: injection, crypto, security, performance, infra, config, dependencies)
4. v0.2.0 published (20 total rules)
5. Full integration testing (workflow E2E, rollback scenario, cache invalidation)

---

## Functional Requirements

### FR-001: GitHub Actions Workflow Integration
- Workflow deve fazer fetch de `/api/v1/rules/latest` na startup
- Timeout: 5 segundos
- Se API falhar: fallback para `.semgrep/theloop-rules.yml.bak` (Phase A rules)
- Logs informativos (fetch attempt, fallback triggered)

### FR-002: JSON → YAML Conversion
- Script: `scripts/json_to_semgrep_yaml.py`
- Input: JSON from API response
- Output: Valid Semgrep YAML
- Validation: Schema check, rule ID uniqueness

### FR-003: 14 New Semgrep Rules
**Injection** (3 rules):
- `path-traversal-001` — Path traversal via string concatenation
- `xxe-001` — XML External Entity (XXE) injection
- `deserialization-001` — Unsafe deserialization (pickle, yaml)

**Crypto** (2 rules):
- `crypto-weak-md5-001` — MD5 for hashing (not encryption)
- `crypto-weak-random-001` — Weak random (Math.random vs crypto.random)

**Security** (3 rules):
- `tls-verify-false-001` — TLS certificate verification disabled
- `jwt-hardcoded-001` — Hardcoded JWT secret
- `cors-wildcard-001` — CORS with wildcard origin

**Performance** (2 rules):
- `sql-timeout-001` — SQL queries without timeout
- `n-plus-one-001` — N+1 query pattern in loops

**Infrastructure** (1 rule):
- `docker-root-001` — Docker container running as root

**Config** (2 rules):
- `hardcoded-url-001` — Hardcoded API/service URLs in code
- `debug-enabled-prod-001` — Debug mode enabled in production

**Dependencies** (1 rule):
- `dependency-vulnerable-001` — Known vulnerable dependencies

### FR-004: Version Pinning Support
- Optional: `THELOOP_RULES_VERSION` env var in workflow
- If set: fetch specific version instead of latest
- Example: `THELOOP_RULES_VERSION=0.1.0`

### FR-005: Cache Invalidation on Publish
- When v0.2.0 published via `POST /api/v1/rules/publish`
- API cache invalidated immediately (verified: GET /latest returns new version)

### FR-006: Rollback Support
- Can deprecate v0.2.0 and reactivate v0.1.0
- Workflow falls back automatically to latest active

---

## Success Criteria

### SC-001: Workflow Fetch
- Endpoint called within 1 second (timeout: 5s)
- Fallback triggers on timeout or HTTP 5xx
- Logs captured in workflow output

### SC-002: JSON → YAML Conversion
- Output valid Semgrep YAML (passes `semgrep --validate`)
- All 14 rules included in output
- Rule IDs unique, no duplicates

### SC-003: 14 Rules Deployed
- All 14 rules in v0.2.0 (20 total with Phase A 6)
- Each rule has test patterns (bad/ + good/)
- Coverage: bad patterns detected, good patterns ignored

### SC-004: API Integration E2E
- Workflow fetches v0.2.0
- Scan runs successfully
- Comment on PR with findings

### SC-005: Rollback Scenario
- Publish v0.2.0 with intentional bad rule
- Deprecate v0.2.0
- Reactivate v0.1.0
- Workflow automatically uses v0.1.0

### SC-006: Performance
- Workflow total time <30s (fetch + convert + scan)
- Cache hit: subsequent runs <5s faster

---

## User Stories

### US-001: GitHub Actions Maintainer
**As a** GitHub Actions maintainer  
**I want to** fetch rules from The Loop API  
**So that** rules are always up-to-date without re-deploying projects

**Acceptance Criteria**:
- Workflow fetches `/api/v1/rules/latest` on each PR
- Fallback to Phase A rules if API unavailable
- No manual updates to `.semgrep/theloop-rules.yml` needed

### US-002: Security Rules Author
**As a** security rules author  
**I want to** add 14 new detection rules  
**So that** more incident patterns are caught at static analysis time

**Acceptance Criteria**:
- All 14 rules published in v0.2.0
- Each rule tested with good/bad patterns
- Rules are discoverable via API

### US-003: DevOps Engineer
**As a** DevOps engineer  
**I want to** pin rule versions in my workflow  
**So that** I can control when new rules are adopted

**Acceptance Criteria**:
- `THELOOP_RULES_VERSION` env var supported
- Can pin to v0.1.0 or v0.2.0
- Unpinned defaults to latest active

### US-004: Release Manager
**As a** release manager  
**I want to** publish new rule versions  
**So that** teams adopt the rules on their own schedule

**Acceptance Criteria**:
- `POST /api/v1/rules/publish` works for v0.2.0
- Can deprecate old versions if needed
- Workflow automatically picks up active version

---

## Edge Cases & Error Handling

### E-001: API Timeout
- If fetch > 5 seconds: use fallback `.semgrep/theloop-rules.yml.bak`
- Log: "API timeout, using Phase A backup rules"

### E-002: API 5xx Error
- If HTTP 500/503: use fallback
- Log: "API error (500), using Phase A backup rules"

### E-003: Invalid JSON
- If JSON response malformed: skip conversion, use Phase A backup
- Log: "Invalid JSON from API, using Phase A backup"

### E-004: Bad Semgrep YAML
- If conversion fails validation: reject, use Phase A backup
- Log: "YAML validation failed, using Phase A backup"

### E-005: Rule ID Conflict
- If 14 new rules have duplicate IDs with Phase A: reject publish
- Error: "Rule ID conflict with existing rules"

### E-006: Network Unavailable
- Workflow fails gracefully: use Phase A rules
- No blocking failures

---

## Testing Strategy

### Unit Tests
- `test_json_to_semgrep_yaml.py`: JSON conversion logic, validation

### Integration Tests
- Fetch API + convert YAML
- Workflow simulation: fetch → convert → scan → comment
- Rollback: deprecate v0.2.0, fetch v0.1.0

### E2E Tests
- Real GitHub Actions run
- PR comment verification
- Merge block on ERROR findings

---

## File Structure

```
specs/012-phase-b-workflow-integration/
  ├── spec.md (this file)
  ├── plan.md (architecture, tech decisions)
  ├── tasks.md (48 tasks, 6 phases)
  └── CLAUDE.md (tech guide, patterns)

.github/workflows/
  └── theloop-guard.yml (UPDATED: fetch from API)

scripts/
  └── json_to_semgrep_yaml.py (NEW: JSON → YAML)

.semgrep/
  └── theloop-rules.yml (UPDATED: v0.2.0 rules)

specs/011-phase-b-api-integration/
  └── (existing Phase B API spec — reference)
```

---

## Acceptance Criteria (Overall)

- ✅ Workflow fetches v0.2.0 from API
- ✅ Fallback to Phase A rules if API down
- ✅ 14 new rules published and tested
- ✅ v0.2.0 with 20 total rules deployed
- ✅ Rollback scenario tested
- ✅ E2E workflow integration verified
- ✅ All tests passing (coverage ≥80%)
- ✅ Documentation complete

---

**Referência**: specs/011-phase-b-api-integration/ (Phase B API — Base)  
**Próxima**: specs/013-phase-c-redis-scaling (Phase C — Redis caching)
