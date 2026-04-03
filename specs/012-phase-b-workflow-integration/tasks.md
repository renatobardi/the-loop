# Phase 5 — Workflow Integration & 14 New Rules (Task Breakdown)

**Total Tasks**: 65 across 6 phases  
**Parallelization Opportunities**: Multiple marked [P] within phases  
**Estimated Timeline**: 8-11 dias  
**MVP Scope**: Phase 1-3 (workflow + rules definition) + Phase 6 (docs + merge)

---

## Phase 1: Workflow Infrastructure Setup (T001–T010)

**Goal**: Create GitHub Actions workflow template with API fetch logic, fallback handling, and version pinning support.

**Independent Test Criteria**: 
- Workflow syntax valid (no YAML parse errors)
- Fetch logic accepts 5-second timeout parameter
- Fallback to .bak file path exists and is readable
- THELOOP_API_TOKEN secret placeholder documented

**Tasks**:

- [ ] T001 Create `.github/workflows/theloop-guard.yml` skeleton with fetch step (name, on, permissions, jobs structure)
- [ ] T002 [P] Implement curl fetch from API with 5s timeout, max-time and connect-timeout flags set
- [ ] T003 [P] Add fallback logic to `.semgrep/theloop-rules.yml.bak` when fetch fails (timeout/5xx)
- [ ] T004 [P] Create `.semgrep/theloop-rules.yml.bak` containing Phase A rules (6 rules in YAML format)
- [ ] T005 Add version pinning support via `THELOOP_RULES_VERSION` environment variable (default: 'latest')
- [ ] T006 [P] Implement JSON → YAML conversion step in workflow (call `python3 scripts/json_to_semgrep_yaml.py`)
- [ ] T007 [P] Add Semgrep validation step (semgrep --validate --config .semgrep/theloop-rules.yml)
- [ ] T008 Add Semgrep scan step (semgrep scan --config, --json output to /tmp/semgrep-results.json)
- [ ] T009 [P] Implement PR comment step with findings table (use actions/github-script@v7)
- [ ] T010 Document workflow in .github/workflows/THELOOP_WORKFLOW.md (fetch logic, fallback, version pinning, troubleshooting)

---

## Phase 2: JSON Conversion Utility Implementation (T011–T025)

**Goal**: Build `scripts/json_to_semgrep_yaml.py` utility with full schema validation and error handling.

**Independent Test Criteria**:
- Converts valid Phase A JSON (6 rules) to valid YAML
- Rejects JSON with missing 'rules' key
- Detects and rejects duplicate rule IDs
- Validates metadata, languages, severity fields
- Output passes `semgrep --validate`

**Tasks**:

- [ ] T011 Create `scripts/json_to_semgrep_yaml.py` with main function signature and argparse setup
- [ ] T012 [P] Implement JSON schema validation (check 'rules' key exists, is list, non-empty)
- [ ] T013 [P] Implement rule ID uniqueness check (reject duplicates, raise ValueError with rule ID)
- [ ] T014 [P] Implement required fields validation (id, languages, message, patterns, severity)
- [ ] T015 [P] Implement `_rule_to_yaml()` helper function (convert single rule dict to YAML lines)
- [ ] T016 Implement message text indentation (4-space indent for multiline messages)
- [ ] T017 [P] Implement metadata serialization (string quotes, array format)
- [ ] T018 [P] Implement patterns array conversion (handle pattern-either, pattern-not, pattern-regex)
- [ ] T019 Implement output file writing (use pathlib.Path.write_text())
- [ ] T020 Add comprehensive docstrings with type hints (JSON input/output examples)
- [ ] T021 Test script with Phase A rules (convert existing 6 rules, validate output YAML)
- [ ] T022 [P] Create `tests/unit/scripts/test_json_to_semgrep_yaml.py` with pytest setup
- [ ] T023 [P] Add test: valid JSON conversion (Phase A 6 rules)
- [ ] T024 [P] Add test: missing 'rules' key raises ValueError
- [ ] T025 Add test: duplicate rule IDs detected and rejected

---

## Phase 3: 14 New Semgrep Rules Definition (T026–T050)

**Goal**: Define all 14 new rules with patterns, metadata, and test examples (good/bad code samples).

**Independent Test Criteria**:
- Each rule has valid pattern-either or pattern blocks
- Metadata includes incident_id, category, loop_url, remediation
- Good code samples don't match (negative test pattern-not working)
- Bad code samples do match (positive test patterns working)
- All 20 rules (6 Phase A + 14 Phase B) pass `semgrep --validate`

**Tasks**:

- [ ] T026 Define `path-traversal-001` rule with pattern-either blocks (string concat, f-string, os.path patterns)
- [ ] T027 [P] Add test code: `tests/code_samples/path-traversal.py` (bad: concat, good: pathlib.Path.resolve)
- [ ] T028 [P] Define `xxe-001` rule with XML parsing patterns (ElementTree.parse, lxml.etree without defusedxml)
- [ ] T029 [P] Add test code: `tests/code_samples/xxe.py` (bad: ElementTree with URL, good: defusedxml)
- [ ] T030 [P] Define `deserialization-001` rule (pickle.load, yaml.load without safe_load)
- [ ] T031 [P] Add test code: `tests/code_samples/deserialization.py` (bad: pickle/yaml unsafe, good: safe variants)
- [ ] T032 [P] Define `crypto-weak-md5-001` rule (hashlib.md5() for hashing, not crypt)
- [ ] T033 [P] Add test code: `tests/code_samples/crypto-weak-md5.py` (bad: hashlib.md5, good: hashlib.sha256 + salt)
- [ ] T034 [P] Define `crypto-weak-random-001` rule (Math.random, random.random without secrets.token_*)
- [ ] T035 [P] Add test code: `tests/code_samples/crypto-weak-random.py` (bad: random/Math.random, good: secrets.token_bytes)
- [ ] T036 [P] Define `tls-verify-false-001` rule (verify=False, ssl._create_unverified_context, NODE_TLS_REJECT_UNAUTHORIZED=0)
- [ ] T037 [P] Add test code: `tests/code_samples/tls-verify-false.py` (bad: verify=False, good: requests with certs)
- [ ] T038 [P] Define `jwt-hardcoded-001` rule (pattern-regex for JWT secret variables with alphanumeric values)
- [ ] T039 [P] Add test code: `tests/code_samples/jwt-hardcoded.py` (bad: SECRET = "key...", good: os.environ['SECRET'])
- [ ] T040 [P] Define `cors-wildcard-001` rule (Access-Control-Allow-Origin: *, CORS middleware with allowedOrigins: *)
- [ ] T041 [P] Add test code: `tests/code_samples/cors-wildcard.py` (bad: "*", good: specific domain list)
- [ ] T042 [P] Define `sql-timeout-001` rule (cursor.execute or query without timeout parameter)
- [ ] T043 [P] Add test code: `tests/code_samples/sql-timeout.py` (bad: no timeout, good: timeout=30)
- [ ] T044 [P] Define `n-plus-one-001` rule (query inside loop, cursor.execute in for loop)
- [ ] T045 [P] Add test code: `tests/code_samples/n-plus-one.py` (bad: query in loop, good: batch query before loop)
- [ ] T046 [P] Define `docker-root-001` rule (USER root or missing USER in Dockerfile)
- [ ] T047 [P] Add test code: `tests/code_samples/Dockerfile.bad` (bad: USER root, good: USER appuser)
- [ ] T048 [P] Define `hardcoded-url-001` rule (pattern-regex for API_URL = "http://...", hardcoded domains)
- [ ] T049 [P] Add test code: `tests/code_samples/hardcoded-url.py` (bad: hardcoded URL, good: os.environ)
- [ ] T050 [P] Define `debug-enabled-prod-001` rule (DEBUG = True, debug: true in code, FLASK_DEBUG=1)

---

## Phase 4: Rule Compilation & Integration Testing (T051–T057)

**Goal**: Compile all 20 rules into `.semgrep/theloop-rules.yml`, verify with semgrep, test end-to-end workflow.

**Independent Test Criteria**:
- All 20 rules (Phase A + Phase B) compile to valid YAML
- `semgrep --validate --config .semgrep/theloop-rules.yml` passes
- Workflow can fetch, convert, validate without errors
- Bad code samples trigger expected rules, good samples don't

**Tasks**:

- [ ] T051 Create `.semgrep/theloop-rules.yml` with all 20 rules (6 Phase A + 14 Phase B) in single YAML file
- [ ] T052 Run `semgrep --validate --config .semgrep/theloop-rules.yml` locally and fix any YAML syntax errors
- [ ] T053 [P] Run `semgrep scan --config .semgrep/theloop-rules.yml tests/code_samples/` and verify bad samples trigger expected rules
- [ ] T054 [P] Run `semgrep scan --config .semgrep/theloop-rules.yml tests/code_samples/` and verify good samples don't trigger
- [ ] T055 Test workflow locally: `python3 scripts/json_to_semgrep_yaml.py --input /tmp/rules.json --output /tmp/test.yml` with Phase A JSON
- [ ] T056 Create unit test file `tests/unit/scripts/test_json_to_semgrep_yaml.py` with pytest parametrize for all 14 new rules
- [ ] T057 Run full test suite: `pytest tests/unit/scripts/test_json_to_semgrep_yaml.py -v` (all tests pass)

---

## Phase 5: API Integration Testing & Rollback Scenarios (T058–T065)

**Goal**: Test workflow fetch from API, version pinning, fallback, and deprecation/rollback flow.

**Independent Test Criteria**:
- Workflow fetches from API /latest endpoint successfully
- Workflow falls back to .bak when API times out (>5s)
- Workflow falls back to .bak when API returns 500
- Version pinning works (THELOOP_RULES_VERSION=0.1.0 fetches specific version)
- Deprecating v0.2.0 causes subsequent fetches to return v0.1.0

**Tasks**:

- [ ] T058 Create `tests/integration/test_workflow_integration.py` with pytest async fixtures (mock API)
- [ ] T059 [P] Add test: API fetch success → workflow uses fetched rules (mock 200 response)
- [ ] T060 [P] Add test: API timeout (>5s) → fallback to .bak used (mock timeout)
- [ ] T061 [P] Add test: API 500 error → fallback to .bak used (mock 500)
- [ ] T062 [P] Add test: Invalid JSON response → fallback to .bak used (malformed JSON)
- [ ] T063 Add test: Invalid YAML from conversion → fallback to .bak used (json_to_semgrep_yaml raises exception)
- [ ] T064 Create `tests/integration/test_rollback_scenario.py` with real API calls (requires live API)
- [ ] T065 [P] Add test: Publish v0.2.0 → deprecate v0.2.0 → fetch /latest returns v0.1.0

---

## Phase 6: Documentation, Code Review & Merge (T066–T080)

**Goal**: Document workflow patterns, create rules catalog, pass code review, merge to main.

**Independent Test Criteria**:
- All tests pass (65 tests total)
- Code coverage ≥ 80% (scripts/ and tests/integration/)
- Ruff lint: 0 errors
- mypy strict: 0 errors
- All documentation complete (CLAUDE.md, THELOOP_RULES_v0.2.0.md, workflow docs)
- PR reviewed and approved
- CI gates pass before merge

**Tasks**:

- [ ] T066 Create `specs/012-phase-b-workflow-integration/CLAUDE.md` with workflow patterns (fetch + fallback, version pinning, cache invalidation)
- [ ] T067 Create `THELOOP_RULES_v0.2.0.md` with catalog of all 20 rules (incident_id, category, severity, remediation for each)
- [ ] T068 [P] Update `.github/workflows/THELOOP_WORKFLOW.md` with troubleshooting section (fetch timeout, invalid YAML, duplicate IDs, fallback issues)
- [ ] T069 [P] Update main `THELOOP.md` (installation guide) to mention v0.2.0 and 14 new rules
- [ ] T070 Run full test suite: `pytest tests/ --cov=scripts --cov=tests/integration --cov-report=term-missing --cov-fail-under=80`
- [ ] T071 [P] Run ruff lint: `ruff check scripts/ tests/` (zero errors)
- [ ] T072 [P] Run mypy strict: `mypy scripts/ --strict` (zero errors)
- [ ] T073 Commit all changes: Phase 5 implementation complete (workflow + 14 rules + tests)
- [ ] T074 Create PR to main with description linking to spec.md, plan.md, tasks.md
- [ ] T075 [P] Self-review code: Check for security issues (API token handling, pattern injection), performance (regex complexity), consistency with Phase B patterns
- [ ] T076 Wait for external code review and approval
- [ ] T077 [P] Make requested changes (if any) and re-push
- [ ] T078 Merge PR to main (squash or merge, per project convention)
- [ ] T079 [P] Deploy workflow to production: Copy `.github/workflows/theloop-guard.yml` to live GitHub Actions (if not auto-deployed via merge)
- [ ] T080 Verify production: Run test PR against main branch with live workflow (one real PR, verify findings comment appears)

---

## Parallelization Opportunities

### Within Phase 1 (Workflow Infrastructure)
- T002-T003: Fetch + fallback logic can be coded in parallel (different code blocks)
- T002, T004: Fetch logic and backup file creation independent
- T006-T009: JSON conversion, validation, scan, and comment steps independent

### Within Phase 3 (Rules Definition)
- **Maximum Parallelization**: All 14 rule definitions (T026-T050) can be coded independently:
  - T026-T027: path-traversal-001
  - T028-T029: xxe-001
  - T030-T031: deserialization-001
  - T032-T033: crypto-weak-md5-001
  - T034-T035: crypto-weak-random-001
  - T036-T037: tls-verify-false-001
  - T038-T039: jwt-hardcoded-001
  - T040-T041: cors-wildcard-001
  - T042-T043: sql-timeout-001
  - T044-T045: n-plus-one-001
  - T046-T047: docker-root-001
  - T048-T049: hardcoded-url-001
  - T050: debug-enabled-prod-001
  - All pairs [P] marked for parallel execution

### Within Phase 4 (Testing)
- T053-T054: Run positive and negative tests (parallel)

### Within Phase 5 (Integration Testing)
- T059-T062: Mock API tests can run in parallel (different test methods)

### Within Phase 6 (Documentation & Merge)
- T066-T069: Documentation writing (multiple files)
- T071-T072: Ruff and mypy linting (parallel)
- T075, T077: Self-review and requested changes (sequential after PR)

---

## Critical Path (Dependency Graph)

```
Phase 1 ✓ (T001–T010)
  ↓
Phase 2 ✓ (T011–T025)
  ↓
Phase 3 ✓ (T026–T050) [Blocks Phase 4 validation]
  ↓
Phase 4 ✓ (T051–T057) [Validates rules]
  ↓
Phase 5 ✓ (T058–T065) [Tests workflow integration]
  ↓
Phase 6 ✓ (T066–T080) [Docs, review, merge]
```

**Sequential Dependency**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6

**Parallelization Potential**: ~70% of tasks within each phase (marked [P]) can run in parallel.

---

## MVP Scope (Minimal Viable Product)

For quick Phase 5 delivery (~8 days), prioritize:

**Must Complete**:
- T001–T010: Workflow infrastructure
- T026–T035: First 5 rules (injection, crypto foundations)
- T051–T057: Rule compilation + validation
- T066–T080: Docs + merge (especially T070 test gate)

**Nice to Have** (Phase 5.1):
- T036–T050: Remaining 9 rules (security, performance, infra, config, dependencies)
- T058–T065: Rollback scenario testing (can be Phase 5.1)

**MVP Acceptance Criteria**:
- ✅ Workflow fetches from API and falls back to .bak
- ✅ JSON → YAML conversion works with Phase A rules
- ✅ First 5 new rules (injection, crypto) defined and tested
- ✅ All tests pass
- ✅ Merged to main

---

## Success Metrics

| Metric | Target | Phase |
|--------|--------|-------|
| Test Coverage | ≥80% | Phase 6 (T070) |
| Ruff Lint Errors | 0 | Phase 6 (T071) |
| Mypy Type Errors | 0 | Phase 6 (T072) |
| Rules Validated | 20/20 | Phase 4 (T052) |
| Bad Samples Caught | 14/14 | Phase 4 (T054) |
| Good Samples Passing | 14/14 | Phase 4 (T054) |
| Workflow E2E Success | 1/1 test PR | Phase 6 (T080) |

---

## Checkpoint Validations

### After Phase 1
- [ ] Workflow YAML syntax valid
- [ ] Fetch step accepts timeout parameter
- [ ] Fallback path exists
- [ ] Version pinning template documented

### After Phase 2
- [ ] json_to_semgrep_yaml.py converts Phase A rules to valid YAML
- [ ] Unit tests written and passing (T022-T025)
- [ ] Output validates with semgrep

### After Phase 3
- [ ] All 14 rules defined with patterns
- [ ] Test code samples created (bad + good for each rule)
- [ ] All patterns reviewed for correctness

### After Phase 4
- [ ] All 20 rules compile to single YAML file
- [ ] `semgrep --validate` passes
- [ ] Bad samples trigger expected rules
- [ ] Good samples don't trigger false positives

### After Phase 5
- [ ] API fetch tested (with timeout + fallback)
- [ ] Version pinning tested
- [ ] Rollback scenario tested
- [ ] Integration tests all passing

### After Phase 6
- [ ] Test coverage ≥80%
- [ ] Ruff lint: 0 errors
- [ ] Mypy strict: 0 errors
- [ ] PR approved and merged
- [ ] Live workflow verified on test PR

---

## Implementation Notes

- **Python Version**: 3.12+ (match backend)
- **Type Hints**: All functions (json_to_semgrep_yaml.py, test files)
- **Async Pattern**: Use asyncio for API tests (Phase 5)
- **Error Handling**: Try/except with specific exception types (json.JSONDecodeError, ValueError, etc.)
- **Import Organization**: Sort alphabetically, no `__future__` imports (conflicts with slowapi)
- **Code Style**: Ruff (strict rules) + mypy (strict mode) + Black (formatting)
- **Test Framework**: pytest (unit) + pytest-asyncio (integration)
- **Mock Library**: unittest.mock.patch for API mocking (Phase 5)

---

**Reference**: specs/011-phase-b-api-integration/tasks.md (74 tasks, similar structure)  
**Next Phase**: specs/013-phase-c-redis-scaling (Phase C — Redis caching optimization)
