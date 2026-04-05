# Tasks: Spec-017 (Multi-Language Rules Expansion)

**Feature**: Expand Semgrep rules from 45 to 123 rules across 7 languages (Python, JavaScript, TypeScript, Java, C#, Go, PHP, Ruby, Kotlin, Rust, C/C++)

**Status**: Phased implementation across 7 phases (30-35 days estimated)

---

## Phase 1: Setup & Planning (Foundational)

- [ ] T001 Review spec-017 and plan.md for completeness
- [ ] T002 Create migration template and validate idempotency pattern
- [ ] T003 Set up test data directory structure: `apps/api/tests/test-data/{bad,good}/{python,java,csharp,go,php,ruby,kotlin,rust,c}/`
- [ ] T004 Validate Semgrep 1.157.0 compatibility and rule syntax

**Test Criteria:**
- All test directories exist
- Semgrep validates empty rule file successfully
- Migration template compiles without errors

---

## Phase 2: Java Rules (15 rules) — [COMPLETE]

- [ ] T005 Implement 15 Java security rules in migration 016_add_java_rules.py
- [ ] T006 Create Java bad test files (5 files: SQL injection, weak crypto, hardcoded secrets, unsafe deser, shell exec)
- [ ] T007 Create Java good test files (2 files: secure JDBC, secure crypto)
- [ ] T008 Validate migration 016 appends rules correctly (45 + 15 = 60)
- [ ] T009 Scan bad Java files and verify 6 findings detected
- [ ] T010 Scan good Java files and verify 0 false positives

**Test Criteria:**
- Bad files trigger: java-crypto-001 (2), java-security-001 (2), java-security-003 (1), java-injection-004 (1)
- Good files trigger: 0 findings
- Migration 016 increases rule count from 45 → 60

---

## Phase 3: C# Rules (15 rules) — [IN PROGRESS]

- [ ] T011 Implement 15 C# security rules in migration 017_add_csharp_rules.py
- [ ] T012 Add missing 2 C# rules to YAML: csharp-injection-003, csharp-security-004
- [ ] T013 Create C# bad test files (3 files: SQL injection, weak crypto, hardcoded secrets)
- [ ] T014 Create C# good test files (1 file: secure parameterized queries, SHA256, TLS validation)
- [ ] T015 Validate migration 017 appends rules correctly (60 + 15 = 75)
- [ ] T016 Scan bad C# files and verify 6 findings detected
- [ ] T017 Scan good C# files and verify 0 false positives

**Test Criteria:**
- Bad files trigger: csharp-crypto-001 (1), csharp-crypto-002 (1), csharp-security-001 (2), csharp-linq-001 (1), csharp-sql-001 (0, covered by LINQ)
- Good files trigger: 0 findings
- Migration 017 increases rule count from 60 → 75

---

## Phase 4: PHP Rules (12 rules)

- [ ] T018 Implement 12 PHP security rules (injection, crypto, security, performance)
- [ ] T019 Create migration 018_add_php_rules.py (75 + 12 = 87 rules)
- [ ] T020 Create PHP bad/good test files
- [ ] T021 Validate migration and test data

---

## Phase 5: Ruby Rules (10 rules)

- [ ] T022 Implement 10 Ruby security rules
- [ ] T023 Create migration 019_add_ruby_rules.py (87 + 10 = 97 rules)
- [ ] T024 Create Ruby bad/good test files
- [ ] T025 Validate migration and test data

---

## Phase 6: Kotlin Rules (8 rules)

- [ ] T026 Implement 8 Kotlin security rules
- [ ] T027 Create migration 020_add_kotlin_rules.py (97 + 8 = 105 rules)
- [ ] T028 Create Kotlin bad/good test files
- [ ] T029 Validate migration and test data

---

## Phase 7: Rust & C/C++ Rules (13 rules)

- [ ] T030 Implement 5 Rust security rules
- [ ] T031 Implement 8 C/C++ security rules
- [ ] T032 Create migration 021_add_rust_cpp_rules.py (105 + 13 = 118 rules)
- [ ] T033 Create Rust/C/C++ bad/good test files
- [ ] T034 Validate migration and test data

---

## Phase 8: Integration & Finalization

- [ ] T035 Update `.semgrep/theloop-rules.yml.bak` with final 123 rules
- [ ] T036 Run full semgrep validation: `semgrep --validate --config .semgrep/theloop-rules.yml`
- [ ] T037 Run full scan of all test-data/ to verify findings
- [ ] T038 Create PR from feat/017-rules-expansion → main
- [ ] T039 Verify CI passes (ruff, mypy, pytest, Trivy, docs-check)
- [ ] T040 Merge to main and deploy to production

**Test Criteria:**
- All 123 rules validate without errors
- All bad test files trigger expected findings
- All good test files trigger 0 false positives
- CI gates pass
- Production deployment successful

---

## Dependencies & Constraints

**Blocking Dependencies:**
- T004 blocks all rule implementation (Semgrep validation)
- T002 blocks all migrations (template pattern)
- Phase 2 (T005-T010) must complete before Phase 3 (migrations are sequential)

**Non-Blocking (Can Run in Parallel):**
- T005, T006, T007 can run in parallel (same phase)
- Phases 4-7 can start once Phase 3 migrations are in place

**Time Estimate by Phase:**
- Phase 1: 1 day (setup)
- Phase 2: 2-3 days (Java, 15 rules + test data)
- Phase 3: 2-3 days (C#, 15 rules + test data)
- Phase 4: 1-2 days (PHP, 12 rules + test data)
- Phase 5: 1-2 days (Ruby, 10 rules + test data)
- Phase 6: 1 day (Kotlin, 8 rules + test data)
- Phase 7: 2 days (Rust + C/C++, 13 rules + test data)
- Phase 8: 2-3 days (integration + deployment)

**Total: ~15-21 days**

---

## Test Strategy

**Per-Phase Testing:**
1. Validate rule count increases correctly (migration idempotency)
2. Scan bad test files and verify findings match expected rules
3. Scan good test files and verify 0 false positives
4. Run semgrep --validate to ensure YAML syntax is correct

**Final Validation (Phase 8):**
- `semgrep --validate --config .semgrep/theloop-rules.yml` → 0 errors, 123 rules
- `semgrep scan --config .semgrep/theloop-rules.yml apps/api/tests/test-data/bad/` → all expected findings triggered
- `semgrep scan --config .semgrep/theloop-rules.yml apps/api/tests/test-data/good/` → 0 findings

---

## Notes

- Each migration follows idempotency pattern from migration 015 and 016
- Each migration APPENDS rules (not overwrites) to support incremental rollout
- All migrations must call `connection.commit()` after DML (CLAUDE.md: feedback_transaction_commits)
- Test data must demonstrate each rule's detection capability
