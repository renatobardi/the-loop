# Tasks: Multi-Language Rules Expansion (Spec-018)

**Feature**: Multi-Language Rules Expansion  
**Branch**: `feat/018-multi-lang-rules`  
**Total Tasks**: 72 (4 setup + 64 language phases + 4 verification)  
**Estimated Duration**: 30–35 days (7 sequential language phases)  
**Status**: Ready for Phase 1 (Java)

---

## Overview

This task list organizes 72 implementation tasks across **9 phases**:

- **Phase 1** (Setup): 4 tasks — project initialization
- **Phases 2–8** (Language Phases): 64 tasks (10 Java + 9×6 other languages = 64)
  - Each phase: write rules → validate → test data → migration → merge
- **Phase 9** (Final): 4 tasks — cross-cutting verification and spec updates

**Dependency Graph**:
```
Phase 1 (Setup)
    ↓
[Phase 2 (Java) → Phase 3 (C#) → Phase 4 (PHP) → Phase 5 (Ruby) → Phase 6 (Kotlin) → Phase 7 (Rust) → Phase 8 (C/C++)]
    ↓
Phase 9 (Final Verification)
```

**Parallelization**: Within each phase, test data tasks [P] can run in parallel. However, language phases must be **sequential** (Phase 2 must complete before Phase 3 starts) to maintain incremental rule count validation.

**MVP Scope**: For a minimal viable product, complete **Phase 1 + Phase 2 (Java)** only. This delivers 15 new Java rules (60 total), validates the pattern for remaining 6 languages, and unblocks the rest.

---

## Requirement Traceability

| Functional Requirement | Coverage | Task IDs |
|------------------------|----------|----------|
| **FR-001** (8–15 rules per language) | ✅ | T005, T015, T024, T033, T042, T051, T060 (rule-writing tasks per language) |
| **FR-002** (semgrep --validate) | ✅ | T008, T018, T027, T036, T045, T054, T063, T069 (validation per language + final check) |
| **FR-003** (categorize rules) | ✅ | T005–T068 (all rule tasks include metadata.category) |
| **FR-004** (CWE identifiers) | ✅ | T005–T068 (all rule tasks include metadata.cwe) |
| **FR-005** (severity levels) | ✅ | T005–T068 (all rule tasks assign ERROR or WARNING) |
| **FR-006** (test data) | ✅ | T006–T007, T016–T017, T025–T026, T034–T035, T043–T044, T052–T053, T061–T062 |
| **FR-007** (idempotent migrations) | ✅ | T011, T021, T030, T039, T048, T057, T066 (with idempotency guard pattern) |
| **FR-008** (.bak sync) | ✅ | T013, T023, T032, T041, T050, T059, T068 |
| **FR-009** (API /rules/latest) | ✅ Implicit | T070 (existing infra; verification only) |
| **FR-010** (web UI /rules/) | ✅ Implicit | T070 (existing infra; verification only) |

| Success Criterion | Coverage | Task IDs |
|-------------------|----------|----------|
| **SC-001** (78 new rules) | ✅ | T005–T068 (15+15+10+10+10+8+10=78) |
| **SC-002** (0 validation errors) | ✅ | T008, T018, T027, T036, T045, T054, T063, T069 |
| **SC-003** (100% bad trigger, 0 FP good) | ✅ | T009–T010, T019–T020, T028–T029, T037–T038, T046–T047, T055–T056, T064–T065 |
| **SC-004** (7 migrations idempotent) | ✅ | T011, T021, T030, T039, T048, T057, T066 |
| **SC-005** (rule browser 123 rules) | ✅ | T070 (verification) |
| **SC-006** (CI gates pass) | ✅ | T014, T023, T032, T041, T050, T059, T068 |
| **SC-007** (v0.4.0 row in DB) | ✅ | T069–T070 |
| **SC-008** (30-sec discovery) | ✅ | T070 (UX verification) |

---

## Phase 1: Setup & Foundation (4 tasks, ~2 days)

Establish branch, infrastructure, and validation patterns.

- [ ] T001 Create feature branch `feat/018-multi-lang-rules` from `main`
- [ ] T002 Verify Semgrep 1.157.0+ is installed and all 7 target languages are supported via `semgrep --version`
- [ ] T003 Create test data directory structure: `apps/api/tests/test-data/bad/{java,csharp,php,ruby,kotlin,rust,cpp}` and `apps/api/tests/test-data/good/{java,csharp,php,ruby,kotlin,rust,cpp}`
- [ ] T004 Document migration template pattern in `apps/api/alembic/versions/_MIGRATION_TEMPLATE.txt` (idempotency guard, rule validation, error handling)

---

## Phase 2: Java Rules (10 tasks, ~5–6 days)

**User Story**: Java Development Team Detects SQL Injection Vulnerabilities (US1, P1)

**Goal**: Add 15 Java-specific rules for injection, cryptography, and security vulnerabilities; validate all test patterns; deploy via migration 016.

**Independent Test Criteria**:
- ✅ `semgrep --validate --config .semgrep/theloop-rules.yml` passes with 0 errors
- ✅ All 5–8 bad test files in `tests/test-data/bad/java/` trigger at least one rule
- ✅ All 2–3 good test files in `tests/test-data/good/java/` produce 0 false positives
- ✅ Migration 016 runs idempotently without error
- ✅ Database row for v0.4.0 contains all 60 rules (45 existing + 15 new)

**Tasks**:

- [ ] T005 [US1] Write 15 Java rules to `.semgrep/theloop-rules.yml` (append-only; update file header to v0.4.0)
  - Rules: `java-injection-001` through `java-injection-005`, `java-crypto-001` through `java-crypto-003`, `java-security-001` through `java-security-004`, `java-perf-001`, `java-config-001`, `java-config-002`
  - Each rule: id, languages, message, severity, patterns, metadata (category, cwe)
  - Reference: `specs/018-multi-lang-rules/contracts/rule-schema.md`
- [ ] T006 [P] [US1] Create test data: bad examples in `apps/api/tests/test-data/bad/java/` (5–8 files, <1KB each)
  - Examples: SQL concatenation, JDBC injection, hardcoded credentials, weak crypto, path traversal, shell injection, unsafe deserialization
- [ ] T007 [P] [US1] Create test data: good examples in `apps/api/tests/test-data/good/java/` (2–3 files, <1KB each)
  - Examples: PreparedStatement, parameterized queries, proper credential handling, strong crypto
- [ ] T008 [US1] Validate Java rules via `semgrep --validate --config .semgrep/theloop-rules.yml` — must pass with 0 errors
- [ ] T009 [US1] Scan bad test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/bad/java/` — verify all files trigger at least one rule, document rule coverage matrix
- [ ] T010 [US1] Scan good test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/good/java/` — verify 0 findings, confirm <5% FP rate acceptable
- [ ] T011 [US1] Create Alembic migration `apps/api/alembic/versions/016_add_java_rules.py` (idempotent, hardcoded 60 rules, UPDATE rule_versions SET rules_json WHERE version='v0.4.0')
- [ ] T012 [US1] Run migration locally: `cd apps/api && alembic upgrade head` — verify no errors, database row updated with 60 rules
- [ ] T013 [US1] Update `.semgrep/theloop-rules.yml.bak` to match v0.4.0 with all 60 rules: `cp .semgrep/theloop-rules.yml .semgrep/theloop-rules.yml.bak`
- [ ] T014 [US1] Create PR from `feat/018-multi-lang-rules` → `main`, verify CI gates pass (ruff, mypy, pytest ≥80%, Trivy, docs-check), merge to main

---

## Phase 3: C# Rules (9 tasks, ~5–6 days)

**User Story**: C# Team Ensures LINQ Injection Prevention (US2, P1)

**Goal**: Add 15 C#-specific rules for SQL injection, LINQ injection, cryptography, and security; validate test patterns; deploy via migration 017.

**Independent Test Criteria**:
- ✅ All 5–8 bad test files in `tests/test-data/bad/csharp/` trigger at least one rule
- ✅ All 2–3 good test files in `tests/test-data/good/csharp/` produce 0 false positives
- ✅ Migration 017 runs without error; database contains 75 rules total
- ✅ API `/rules/latest` returns `rules_count: 75`

**Tasks**:

- [ ] T015 [US2] Write 15 C# rules to `.semgrep/theloop-rules.yml` (append to existing Java rules)
  - Rules: `csharp-sql-001` through `csharp-sql-003`, `csharp-linq-001` through `csharp-linq-002`, `csharp-crypto-001` through `csharp-crypto-002`, `csharp-security-001` through `csharp-security-003`, `csharp-perf-001`, `csharp-config-001` through `csharp-config-002`
- [ ] T016 [P] [US2] Create test data: bad examples in `apps/api/tests/test-data/bad/csharp/` (5–8 files)
- [ ] T017 [P] [US2] Create test data: good examples in `apps/api/tests/test-data/good/csharp/` (2–3 files)
- [ ] T018 [US2] Validate C# rules via `semgrep --validate --config .semgrep/theloop-rules.yml`
- [ ] T019 [US2] Scan bad test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/bad/csharp/` — all files trigger at least one rule
- [ ] T020 [US2] Scan good test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/good/csharp/` — 0 findings
- [ ] T021 [US2] Create Alembic migration `apps/api/alembic/versions/017_add_csharp_rules.py` (hardcoded 75 rules total, UPDATE rule_versions for v0.4.0)
- [ ] T022 [US2] Run migration locally: `alembic upgrade head` — verify database contains 75 rules
- [ ] T023 [US2] Update `.semgrep/theloop-rules.yml.bak` to v0.4.0 with 75 rules, create PR → main, merge after CI passes

---

## Phase 4: PHP Rules (9 tasks, ~4–5 days)

**User Story**: PHP Application Prevents Command Injection (US3, P2)

**Goal**: Add 10 PHP-specific rules for command injection, weak crypto, and security; deploy via migration 018.

**Independent Test Criteria**:
- ✅ All 4–5 bad test files trigger at least one rule
- ✅ All 2–3 good test files produce 0 false positives
- ✅ Migration 018 runs; database contains 85 rules total

**Tasks**:

- [ ] T024 [US3] Write 10 PHP rules to `.semgrep/theloop-rules.yml`
  - Rules: `php-injection-001` through `php-injection-003`, `php-crypto-001` through `php-crypto-002`, `php-security-001` through `php-security-002`, `php-perf-001`, `php-config-001`
- [ ] T025 [P] [US3] Create test data: bad examples in `apps/api/tests/test-data/bad/php/` (4–5 files)
- [ ] T026 [P] [US3] Create test data: good examples in `apps/api/tests/test-data/good/php/` (2–3 files)
- [ ] T027 [US3] Validate PHP rules via `semgrep --validate`
- [ ] T028 [US3] Scan bad test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/bad/php/`
- [ ] T029 [US3] Scan good test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/good/php/`
- [ ] T030 [US3] Create migration `apps/api/alembic/versions/018_add_php_rules.py` (85 rules total)
- [ ] T031 [US3] Run migration locally; verify 85 rules in database
- [ ] T032 [US3] Update `.semgrep/theloop-rules.yml.bak`, create PR → main, merge

---

## Phase 5: Ruby Rules (9 tasks, ~4–5 days)

**User Story**: Ruby/Rails Team Prevents N+1 Queries (US4, P2)

**Goal**: Add 10 Ruby-specific rules for N+1 queries, weak crypto, and security; deploy via migration 019.

**Independent Test Criteria**:
- ✅ All 4–5 bad test files trigger at least one rule
- ✅ All 2–3 good test files produce 0 false positives
- ✅ Migration 019 runs; database contains 95 rules total

**Tasks**:

- [ ] T033 [US4] Write 10 Ruby rules to `.semgrep/theloop-rules.yml`
  - Rules: `ruby-perf-001` through `ruby-perf-002`, `ruby-crypto-001`, `ruby-security-001` through `ruby-security-003`, `ruby-error-001` through `ruby-error-002`, `ruby-config-001`
- [ ] T034 [P] [US4] Create test data: bad examples in `apps/api/tests/test-data/bad/ruby/` (4–5 files)
- [ ] T035 [P] [US4] Create test data: good examples in `apps/api/tests/test-data/good/ruby/` (2–3 files)
- [ ] T036 [US4] Validate Ruby rules via `semgrep --validate`
- [ ] T037 [US4] Scan bad test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/bad/ruby/`
- [ ] T038 [US4] Scan good test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/good/ruby/`
- [ ] T039 [US4] Create migration `apps/api/alembic/versions/019_add_ruby_rules.py` (95 rules total)
- [ ] T040 [US4] Run migration locally; verify 95 rules in database
- [ ] T041 [US4] Update `.semgrep/theloop-rules.yml.bak`, create PR → main, merge

---

## Phase 6: Kotlin Rules (9 tasks, ~4–5 days)

**User Story**: Kotlin/Coroutine Team Prevents Non-Cancellable Scope Usage (US5, P3)

**Goal**: Add 10 Kotlin-specific rules for coroutines, crypto, and memory safety; deploy via migration 020.

**Independent Test Criteria**:
- ✅ All 4–5 bad test files trigger at least one rule
- ✅ All 2–3 good test files produce 0 false positives
- ✅ Migration 020 runs; database contains 105 rules total

**Tasks**:

- [ ] T042 [US5] Write 10 Kotlin rules to `.semgrep/theloop-rules.yml`
  - Rules: `kotlin-coroutine-001` through `kotlin-coroutine-002`, `kotlin-crypto-001` through `kotlin-crypto-002`, `kotlin-security-001` through `kotlin-security-002`, `kotlin-error-001`, `kotlin-config-001` through `kotlin-config-002`
- [ ] T043 [P] [US5] Create test data: bad examples in `apps/api/tests/test-data/bad/kotlin/` (4–5 files)
- [ ] T044 [P] [US5] Create test data: good examples in `apps/api/tests/test-data/good/kotlin/` (2–3 files)
- [ ] T045 [US5] Validate Kotlin rules via `semgrep --validate`
- [ ] T046 [US5] Scan bad test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/bad/kotlin/`
- [ ] T047 [US5] Scan good test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/good/kotlin/`
- [ ] T048 [US5] Create migration `apps/api/alembic/versions/020_add_kotlin_rules.py` (105 rules total)
- [ ] T049 [US5] Run migration locally; verify 105 rules in database
- [ ] T050 [US5] Update `.semgrep/theloop-rules.yml.bak`, create PR → main, merge

---

## Phase 7: Rust Rules (9 tasks, ~3–4 days)

**User Story**: Rust Library Author Prevents Unsafe Dereference (US6, P3)

**Goal**: Add 8 Rust-specific rules for unsafe blocks, panic handling, and memory safety; deploy via migration 021.

**Independent Test Criteria**:
- ✅ All 3–4 bad test files trigger at least one rule
- ✅ All 2–3 good test files produce 0 false positives
- ✅ Migration 021 runs; database contains 113 rules total

**Tasks**:

- [ ] T051 [US6] Write 8 Rust rules to `.semgrep/theloop-rules.yml`
  - Rules: `rust-unsafe-001` through `rust-unsafe-002`, `rust-error-001` through `rust-error-002`, `rust-crypto-001`, `rust-security-001`, `rust-config-001`
- [ ] T052 [P] [US6] Create test data: bad examples in `apps/api/tests/test-data/bad/rust/` (3–4 files)
- [ ] T053 [P] [US6] Create test data: good examples in `apps/api/tests/test-data/good/rust/` (2–3 files)
- [ ] T054 [US6] Validate Rust rules via `semgrep --validate`
- [ ] T055 [US6] Scan bad test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/bad/rust/`
- [ ] T056 [US6] Scan good test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/good/rust/`
- [ ] T057 [US6] Create migration `apps/api/alembic/versions/021_add_rust_rules.py` (113 rules total)
- [ ] T058 [US6] Run migration locally; verify 113 rules in database
- [ ] T059 [US6] Update `.semgrep/theloop-rules.yml.bak`, create PR → main, merge

---

## Phase 8: C/C++ Rules (9 tasks, ~4–5 days)

**User Story**: C/C++ Team Prevents Buffer Overflow (US7, P3)

**Goal**: Add 10 C/C++-specific rules for buffer overflow, format strings, and memory safety; deploy via migration 022; **pre-merge review required** (FP rate validation).

**Independent Test Criteria**:
- ✅ All 4–5 bad test files trigger at least one rule
- ✅ All 2–3 good test files produce <5% false positives (refine if necessary)
- ✅ Migration 022 runs; database contains 123 rules total
- ✅ **Pre-merge code review**: FP rate must be <5% on test data before merge to main

**Tasks**:

- [ ] T060 [US7] Write 10 C/C++ rules to `.semgrep/theloop-rules.yml`
  - Rules: `cpp-buffer-001` through `cpp-buffer-002`, `cpp-injection-001` through `cpp-injection-002`, `cpp-crypto-001`, `cpp-security-001` through `cpp-security-002`, `cpp-error-001`, `cpp-config-001`
  - **Note**: Use `languages: ["c", "cpp"]` for rules targeting both C99 and C++11+
- [ ] T061 [P] [US7] Create test data: bad examples in `apps/api/tests/test-data/bad/cpp/` (4–5 files)
  - Include: strcpy, gets, format string, unchecked buffer, weak random, hardcoded secrets
- [ ] T062 [P] [US7] Create test data: good examples in `apps/api/tests/test-data/good/cpp/` (2–3 files)
  - Include: strncpy, secure_malloc, format string with %s, proper bounds checking
- [ ] T063 [US7] Validate C/C++ rules via `semgrep --validate`
- [ ] T064 [US7] Scan bad test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/bad/cpp/` — measure FP rate
- [ ] T065 [US7] Scan good test files: `semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/good/cpp/` — document any false positives, refine patterns if >5%
- [ ] T066 [US7] Create migration `apps/api/alembic/versions/022_add_cpp_rules.py` (123 rules total)
- [ ] T067 [US7] Run migration locally; verify 123 rules in database; **flag for pre-merge review if FP rate >5%**
- [ ] T068 [US7] Update `.semgrep/theloop-rules.yml.bak`, create PR → main; **require code review sign-off on FP validation before merge**

---

## Phase 9: Final Verification & Spec Cleanup (4 tasks, ~2 days)

Cross-cutting verification, spec artifacts, and production readiness.

- [ ] T069 Complete end-to-end validation:
  - `semgrep --validate --config .semgrep/theloop-rules.yml` — 0 errors, all 123 rules pass
  - `pytest --cov=src --cov-fail-under=80` — coverage ≥80%
  - `ruff check src/ tests/` — 0 lint violations
  - `mypy src/` — 0 type errors
- [ ] T070 Verify production API (FR-009, FR-010 — existing infrastructure):
  - **Note**: `/api/v1/rules/latest` endpoint and `/rules/` web UI already exist; no new code required. This task validates existing infrastructure now contains all 123 rules.
  - Deploy all 7 migrations to production Cloud Run via `main` merge
  - Call `curl https://api.loop.oute.pro/api/v1/rules/latest | jq '.rules_count'` — confirm **123** rules returned
  - Visit `https://loop.oute.pro/rules/` — confirm all 123 rules display, grouped by language + severity
  - Verify ruleset is discoverable within 30 seconds by browsing (SC-008)
- [ ] T071 Update spec artifacts:
  - Update `specs/018-multi-lang-rules/` with completion notes in plan.md
  - Archive any research/planning documents to `.project/archive/`
  - Verify all 16 checklist items in `checklists/requirements.md` are still ✅
- [ ] T072 Close feature: merge final commits to `main`, update project status in MEMORY.md (Spec-018 COMPLETE)

---

## Implementation Strategy

### Linear Sequential Execution

Each language phase **must** complete fully before the next phase begins. This ensures:

1. **Incremental validation**: Each phase's rules are validated independently; bugs are caught early
2. **Database consistency**: Migrations run in order (016 → 017 → ... → 022); rollback is straightforward
3. **Reduced risk**: No parallel conflicts; clear ordering of changes

### Within Each Phase: Parallelization Opportunities

Tasks T025–T026 (test data creation) and T043–T044 (Kotlin test data) can run in parallel with rule writing (T024, T042), since they depend only on the file paths existing, not the rules being complete.

### MVP Scope (First 2 Weeks)

To deliver value quickly while validating the pattern:

**Minimum Viable Product** = Phase 1 + Phase 2 (Java only)

- **Tasks**: T001–T023 (4 setup + 19 Java-specific tasks)
- **Deliverable**: 60 total rules (45 existing + 15 Java), v0.4.0 ready for C# phase
- **Duration**: ~7 days
- **Benefit**: Immediately unblocks Java users; validates migration/test pattern for remaining languages

### Phase Kickoff Cadence

After MVP (Java) completes:
- **Days 8–13**: C# (Phase 3)
- **Days 14–18**: PHP (Phase 4)
- **Days 19–23**: Ruby (Phase 5)
- **Days 24–28**: Kotlin (Phase 6)
- **Days 29–31**: Rust (Phase 7)
- **Days 32–36**: C/C++ (Phase 8, with pre-merge review)
- **Days 37–38**: Final verification (Phase 9)

---

## Success Metrics

✅ **Task Completion**:
- [ ] All 71 tasks completed and verified
- [ ] Each task has clear acceptance criteria met before marking complete

✅ **Code Quality**:
- [ ] `semgrep --validate` passes with 0 errors
- [ ] `ruff check`, `mypy`, `pytest ≥80%` all pass
- [ ] All 123 rules deployed to production

✅ **Testing & Validation**:
- [ ] 100% of bad test files trigger at least one rule per language
- [ ] 100% of good test files produce 0 false positives (or <5% for C/C++ pre-review)
- [ ] All 7 migrations (016–022) run idempotently without error

✅ **Production Verification**:
- [ ] `/api/v1/rules/latest` returns `rules_count: 123`
- [ ] `/rules/` displays all 123 rules grouped by severity + language
- [ ] Dashboard link to `/rules/` is accessible
- [ ] CI pipeline green on all gates

---

## Notes

- **Idempotency**: Each migration includes an idempotency guard (`if existing_rules and len(existing_rules) >= N: return`). Migrations can be re-run safely without corruption.
- **Rule IDs**: Follow kebab-case format: `{language}-{category}-{number}` (e.g., `java-injection-001`)
- **Test Data Size**: Each file <1KB to keep repo size minimal
- **FP Rate**: Target <5% on all languages; C/C++ requires pre-merge review due to complexity
- **No Schema Changes**: All rules stored as JSON in existing `rule_versions.rules_json` column; no new tables or migrations of `rule_versions` schema itself
- **CI Gates**: All existing gates (ruff, mypy, pytest, Trivy, docs-check) must pass before merge
