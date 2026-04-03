# Tasks-011: Phase B — API Integration + Versionamento

**Total de Tarefas:** 74  
**Organizadas em:** 6 Fases  
**Timeline:** 3-4 semanas

---

## Fase 1: Setup & Infrastructure (T001-T010)

- [x] T001 Create specs/011 directory structure
- [x] T002 Create CLAUDE.md note: Phase B tech decisions
- [x] T003 [P] Install/verify dev dependencies (asyncpg, sqlalchemy 2.0)
- [x] T004 Create Alembic migration scaffold (007-create_rule_versions)
- [x] T005 [P] Setup pre-commit hooks for Phase B work
- [x] T006 Create database schema script (migrations.sql)
- [x] T007 [P] Test Alembic migration locally (test DB)
- [x] T008 Seed v0.1.0 initial data (6 Phase A rules)
- [x] T009 [P] Create .env.example with new vars (API URLs, etc)
- [x] T010 Document Phase B setup steps in THELOOP.md

---

## Fase 2: Database & Domain Layer (T011-T025)

### Database & ORM

- [x] T011 [P] Create RuleVersionRow (SQLAlchemy model) in adapters/postgres/models.py
  - Fields: id (UUID), version (VARCHAR), rules_json (JSONB), created_at, published_by, notes, status, deprecated_at
  - Constraints: semver format, valid_deprecation
  - Indexes: status, version, created_at
  
- [x] T012 [P] Run Alembic migration 007 locally
  - Creates rule_versions table
  - Indexes created
  - Verify: `SELECT * FROM rule_versions;`
  
- [x] T013 [P] Create RuleVersionNotFoundError in domain/exceptions.py
- [x] T014 [P] Create VersionAlreadyExistsError in domain/exceptions.py
- [x] T015 [P] Create InvalidVersionFormatError in domain/exceptions.py

### Domain Models

- [x] T016 Create Rule (Pydantic) in domain/models.py
  - Fields: id, languages, message, severity, metadata, patterns
  - Frozen: True
  
- [x] T017 [P] Create RuleVersionStatus (Enum) in domain/models.py
  - Values: DRAFT, ACTIVE, DEPRECATED
  
- [x] T018 Create RuleVersion (Pydantic) in domain/models.py
  - Fields: id, version, rules, status, created_at, published_by, notes, deprecated_at
  - Validators: semver format
  - Property: rules_count
  - Frozen: True
  
- [x] T019 [P] Add unit tests for Rule (Pydantic)
- [x] T020 [P] Add unit tests for RuleVersion (Pydantic validation, semver)
- [x] T021 [P] Add unit tests for RuleVersionStatus enum

### Repository Pattern

- [x] T022 Create RuleVersionRepository (protocol) in ports/rule_version_repo.py
  - Methods: get_latest_active(), get_by_version(version), list_all(), publish_version(), deprecate_version()
  
- [x] T023 Create PostgresRuleVersionRepository in adapters/postgres/rule_version_repository.py
  - Implement all protocol methods
  - Use _row_to_domain() helper pattern
  - Handle not found errors
  
- [x] T024 [P] Add unit tests for RuleVersionRepository (mocked DB)
- [x] T025 [P] Add integration tests for RuleVersionRepository (real DB)

---

## Fase 3: Service Layer & API Preparation (T026-T035)

- [x] T026 Create RuleVersionService in domain/services.py
  - Methods: get_latest_active(), get_by_version(), list_all(), publish_version(), deprecate_version()
  - Handles exceptions, business logic
  
- [x] T027 [P] Create RuleVersionCache in adapters/postgres/cache.py
  - get_latest(), set_latest(), invalidate()
  - TTL: 300 seconds (5 minutes)
  
- [x] T028 Create request/response models in api/routes/rules.py
  - PublishRulesRequest, RuleVersionResponse, VersionListResponse
  
- [x] T029 [P] Add unit tests for RuleVersionService
- [x] T030 [P] Add unit tests for RuleVersionCache (TTL, expiration)
- [x] T031 [P] Create authentication check: require_admin() in api/deps.py
- [x] T032 Add rate limiting config for rules endpoints (60/min GET, 10/min POST)
- [x] T033 [P] Add unit tests for authentication/authorization
- [x] T034 [P] Create error handling specs (404, 409, 400, 403 responses)
- [x] T035 [P] Document error codes in spec/011/plan.md

---

## Fase 4: API Endpoints (T036-T050)

- [x] T036 Implement GET /api/v1/rules/latest
  - Fetch from cache OR service
  - Return 200 with RuleVersionResponse
  - Set Cache-Control: public, max-age=300
  
- [x] T037 [P] Implement GET /api/v1/rules/{version}
  - Query by specific version (any status)
  - Return 200 or 404
  
- [x] T038 Implement GET /api/v1/rules/versions
  - List all versions with status
  - Return array of version summaries
  
- [x] T039 [P] Implement POST /api/v1/rules/publish (admin)
  - Validate semver
  - Check admin role
  - Publish new version
  - Invalidate cache
  - Return 201 or error
  
- [x] T040 [P] Register routes in main.py (app.include_router)
- [x] T041 Add @limiter.limit() decorator to all endpoints
- [x] T042 [P] Test all 4 endpoints manually (curl)
- [x] T043 [P] Test cache hit (second request <10ms)
- [x] T044 Test error responses (404, 409, 400, 403)
- [x] T045 [P] Test fallback (mock API failure)
- [x] T046 Test rate limiting (>60 requests in 1 min → 429)
- [x] T047 [P] Add API contract tests (request/response schemas)
- [x] T048 Test authentication (missing token → 401)
- [x] T049 [P] Test authorization (non-admin → 403)
- [x] T050 [P] Performance test (latency <100ms uncached, <10ms cached)

---

## Fase 5: Workflow Integration & New Rules (T051-T074)

### Workflow Updates

- [x] T051 Update .github/workflows/theloop-guard.yml
  - Add step: Fetch latest rules from API
  - Add fallback: if API timeout, use .semgrep/theloop-rules.yml.bak
  
- [x] T052 Create scripts/json_to_semgrep_yaml.py
  - Input: JSON from API
  - Output: YAML for Semgrep
  - Validate conversion
  
- [x] T053 [P] Test workflow locally (simulate fetch + scan)
- [x] T054 [P] Test fallback (kill API, verify fallback activates)
- [x] T055 Test version pinning (THELOOP_RULES_VERSION env var)
- [x] T056 [P] Update THELOOP.md workflow examples
- [x] T057 [P] Add to-phase-b migration guide for users

### New Rules (14)

- [x] T058 Create rule: path-traversal-001 (Injection)
- [x] T059 [P] Create rule: xxe-001 (Injection)
- [x] T060 Create rule: deserialization-001 (Injection)
- [x] T061 [P] Create rule: crypto-weak-md5-001 (Crypto)
- [x] T062 Create rule: crypto-weak-random-001 (Crypto)
- [x] T063 [P] Create rule: tls-verify-false-001 (Security)
- [x] T064 Create rule: jwt-hardcoded-001 (Security)
- [x] T065 [P] Create rule: cors-wildcard-001 (Security)
- [x] T066 Create rule: sql-timeout-001 (Performance)
- [x] T067 [P] Create rule: n-plus-one-001 (Performance)
- [x] T068 Create rule: docker-root-001 (Infrastructure)
- [x] T069 [P] Create rule: hardcoded-url-001 (Config)
- [x] T070 Create rule: dependency-vulnerable-001 (Dependencies)
- [x] T071 [P] Create rule: debug-enabled-prod-001 (Config)

### Rules Testing & Deprecate Endpoint

- [x] T072 Test all 14 new rules (bad/ + good/ patterns)
- [x] T073 [P] Publish v0.2.0 (20 total rules: 6 original + 14 new)
  - POST /api/v1/rules/publish
  - Verify: GET /api/v1/rules/latest → rules_count = 20
  
- [x] T074 [P] Implement POST /api/v1/rules/deprecate endpoint + tests

---

## Fase 6: Testing & Documentation (T075-T098)

### Integration Tests

- [x] T075 [P] Test Alembic migration 007 on real Cloud SQL
- [x] T076 Test full workflow: publish v0.2.0 → fetch API → scan → comment
- [x] T077 [P] Test rollback scenario: publish v0.2.0 (bad) → deprecate → activate v0.1.0
- [x] T078 Test cache invalidation (publish → GET latest → cache refreshed)
- [x] T079 [P] Test concurrent requests (5 parallel GET /latest)

### Coverage & Quality

- [x] T080 Run pytest --cov=src --cov-fail-under=80
- [x] T081 [P] Run mypy src/ (strict mode)
- [x] T082 Run ruff check src/ tests/
- [x] T083 [P] Fix any lint/type errors

### Documentation

- [ ] T084 [P] Create API documentation (endpoints, examples, errors)
- [ ] T085 Create versioning strategy guide (semver, deprecation, rollback)
- [ ] T086 [P] Update README.md (Phase B section)
- [ ] T087 Create migration guide (Phase A → Phase B)
- [ ] T088 [P] Update _deepwiki/the-loop/NOTES/spec-011-learnings.md
- [ ] T089 Update _deepwiki/the-loop/ROADMAP.md (Phase C next)
- [ ] T090 [P] Create troubleshooting guide (API down, fallback, etc)

### Code Review & Merge

- [ ] T091 Self-review: check all spec requirements met
- [ ] T092 [P] Create PR feat/phase-b-api-integration
- [ ] T093 Code review (against CONSTITUTION.md, testing, docs)
- [ ] T094 [P] Address review feedback
- [ ] T095 Ensure all CI gates pass
- [ ] T096 [P] Merge PR to main
- [ ] T097 Verify Cloud Run auto-deploy completes
- [ ] T098 [P] Post-mortem: learnings to _deepwiki

---

## Parallelization Opportunities

**Week 1 (Setup):**
- [P] T003, T005, T009 (dependencies, hooks, config)

**Week 2 (Domain):**
- [P] T011-T015 (ORM + exceptions can run in parallel)
- [P] T019-T021 (unit tests can run after models)
- [P] T024-T025 (repository tests after repo created)

**Week 3 (API):**
- [P] T036-T039 (endpoints can be created in parallel)
- [P] T058-T070 (rules can be created in parallel)

**Week 4 (Testing):**
- [P] T075-T079 (integration tests independent)
- [P] T080-T083 (coverage + lint independent)

---

## Acceptance Criteria (Per Task)

**Each task must satisfy:**

```
✅ Code written (if applicable)
✅ Tests added (unit or integration)
✅ Documentation updated
✅ No lint/type errors
✅ CR ready (marked in commit message)
```

**Example commit message:**
```
feat(api): implement GET /api/v1/rules/latest

- Add RuleVersionService.get_latest_active()
- Implement GET /api/v1/rules/latest endpoint
- Add caching (TTL 300s)
- Tests: unit + API contract tests
- Docs: API endpoint reference

Closes T036
```

---

## Checkpoint Validations

**After T010 (Setup):**
- [ ] Alembic migration 007 created
- [ ] v0.1.0 seeded in rule_versions table
- [ ] Dev environment ready (dependencies, hooks)

**After T025 (Domain):**
- [ ] RuleVersion model validated
- [ ] Repository tests pass (mocked + integration)
- [ ] Coverage ≥80%

**After T050 (API):**
- [ ] All 4 endpoints working
- [ ] Cache tested (<10ms hits)
- [ ] Error handling comprehensive

**After T074 (Workflow):**
- [ ] v0.2.0 published (20 rules)
- [ ] Workflow fetches from API
- [ ] Fallback tested

**After T098 (Complete):**
- [ ] All gates pass (lint, type, coverage, security)
- [ ] Documentation complete
- [ ] PR merged, deployed to prod

---

## How to Execute

```bash
# Week 1: Setup
T001-T010

# Week 2: Domain + API prep
T011-T035 (parallel where marked [P])

# Week 3: API + Workflow
T036-T074 (parallel where marked [P])

# Week 4: Testing + Merge
T075-T098 (parallel where marked [P])
```

---

**Status:** Ready for kickoff  
**Estimated effort:** 74 tasks × 30-60 min/task = 37-74 hours (4-5 days intense work)  
**Timeline:** 3-4 weeks (part-time) or 4-5 days (full-time sprint)

---

**Última atualização:** 2026-04-03  
**Próxima atualização:** Após T010 (framework checkpoint)
