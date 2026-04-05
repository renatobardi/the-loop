# Spec-017: Rules Expansion — Detailed Plan

**Spec:** 017 (Rules Expansion — Multi-Language Pack)  
**Branch:** `feat/017-rules-expansion`  
**Depends on:** Spec-016 ✅ merged  
**Duration:** 30–35 days | 7 languages | ~78 rules  
**Target release:** v0.4.0+

---

## Context

Spec-016 delivered the foundation: 45 rules across Python (20 legacy + 6 Phase A), JS/TS (15), and Go (10). Spec-017 expands coverage to the **top 7 additional languages** (Java, C#, PHP, Ruby, Kotlin, Rust, C/C++) with ~10–15 rules each, following the same Semgrep pattern taxonomy established in Phase A–C.

The Loop becomes a **language-agnostic security platform**, covering incident patterns across development ecosystems.

---

## Scope

### Languages (ordered by priority)

| # | Language | Rules | Effort | CWE focus |
|---|----------|-------|--------|-----------|
| 1 | **Java** | 15 | Medium | 89, 502, 327, 295, 798 |
| 2 | **C#** | 15 | Medium | 89, 502, 327, 295, 798 |
| 3 | **PHP** | 10 | Easy-Medium | 89, 502, 327, 345 |
| 4 | **Ruby** | 10 | Easy | 89, 502, 327, 338 |
| 5 | **Kotlin** | 10 | Medium | 89, 502, 327, 295 |
| 6 | **Rust** | 8 | Easy-Medium | 327, 338, 416 |
| 7 | **C/C++** | 10 | Hard | 327, 338, 119 |

**Total:** ~78 rules (+ existing 45 = 123 total)

### Rule Categories (per language)

Every language pack includes (where applicable):

1. **Injection** (3–4 rules)
   - SQL injection (string concat, dynamic queries)
   - Command injection (shell exec with variables)
   - Path traversal (file operations with user input)

2. **Cryptography** (2–3 rules)
   - Weak hashes (MD5, SHA1)
   - Weak random (Math.random, rand, etc. for tokens)
   - Hardcoded secrets/keys

3. **Security** (3–4 rules)
   - TLS verification disabled
   - CORS wildcards
   - JWT hardcoded secrets
   - Unsafe deserialization

4. **Performance** (1–2 rules)
   - N+1 query patterns
   - Unbounded loops with I/O
   - Missing timeouts

5. **Error Handling** (1–2 rules)
   - Silently caught exceptions
   - Panic/crash in handlers
   - Missing validation

6. **Language-Specific** (1–3 rules)
   - Java: JDBC injection, unsafe reflection
   - C#: SQL parameterization, LINQ injection
   - PHP: $_GET/$_POST sanitization
   - Ruby: rack/rails conventions
   - Kotlin: coroutine misuse
   - Rust: unsafe block analysis, panic in lib code
   - C/C++: buffer overflow, format strings, memory leaks

---

## Implementation Phases

### Phase 1: Java (5–6 days) — Priority 1

**Files to create/modify:**
- `.semgrep/theloop-rules.yml` → add 15 Java rules (ids: `java-injection-00{1,2,3}`, `java-jdbc-{01,02}`, `java-crypto-{01,02}`, `java-security-{01,02,03}`, `java-reflection-01`, `java-perf-01`, `java-error-{01,02}`)
- `apps/api/alembic/versions/016_add_java_rules.py` → new migration
- `tests/test-data/bad/java/*.java` (5–8 files)
- `tests/test-data/good/java/*.java` (2–3 files)

**Rules (15):**

| ID | Detects | Severity | CWE |
|---|---|---|---|
| `java-injection-001` | SQL injection via string concat | ERROR | 89 |
| `java-injection-002` | JDBC PreparedStatement not used | ERROR | 89 |
| `java-injection-003` | Command execution with shell | ERROR | 78 |
| `java-jdbc-001` | JDBC executeQuery with user input | ERROR | 89 |
| `java-jdbc-002` | SQL concatenation instead of bind params | ERROR | 89 |
| `java-crypto-001` | MD5 or SHA1 for hashing | WARNING | 327 |
| `java-crypto-002` | java.util.Random for secrets | WARNING | 338 |
| `java-security-001` | TLS verification disabled (UNSAFE_HOST_NAME_VERIFIER) | ERROR | 295 |
| `java-security-002` | Hardcoded API credentials | ERROR | 798 |
| `java-security-003` | Unsafe deserialization (ObjectInputStream) | ERROR | 502 |
| `java-reflection-001` | Unsafe reflection with user input | WARNING | 470 |
| `java-http-001` | HttpClient without timeout | WARNING | – |
| `java-perf-001` | N+1 query in loop (Hibernate) | WARNING | – |
| `java-error-001` | Exception caught but silently ignored | WARNING | – |
| `java-error-002` | System.exit() in library code | WARNING | – |

**Deliverables:**
- `semgrep --validate` passes with 15 rules
- 5–8 bad Java examples (with violations)
- 2–3 good Java examples (compliant)
- Migration 016 idempotent, validates before insert

---

### Phase 2: C# (5–6 days) — Priority 2

**Files:**
- `.semgrep/theloop-rules.yml` → add 15 C# rules (`csharp-injection-*`, `csharp-linq-*`, etc.)
- `apps/api/alembic/versions/017_add_csharp_rules.py`
- `tests/test-data/bad/csharp/*.cs`
- `tests/test-data/good/csharp/*.cs`

**Rules (15):**

| ID | Detects | Severity |
|---|---|---|
| `csharp-injection-001` | SQL injection via string interpolation | ERROR |
| `csharp-injection-002` | Command execution (Process.Start) with args | ERROR |
| `csharp-linq-001` | LINQ query injection (dynamic expressions) | ERROR |
| `csharp-sql-001` | SqlCommand without parameterized query | ERROR |
| `csharp-sql-002` | SqlDataReader without try-finally | WARNING |
| `csharp-crypto-001` | MD5/SHA1 for hashing | WARNING |
| `csharp-crypto-002` | Random() for security tokens | WARNING |
| `csharp-security-001` | ServicePointManager.ServerCertificateValidationCallback ignored | ERROR |
| `csharp-security-002` | Hardcoded connection strings | ERROR |
| `csharp-security-003` | BinaryFormatter deserialization | ERROR |
| `csharp-aspnet-001` | ViewBag/ViewData without encoding | ERROR |
| `csharp-aspnet-002` | ValidateInput(false) on controller | WARNING |
| `csharp-async-001` | async void event handlers (fire-and-forget) | WARNING |
| `csharp-error-001` | Empty catch blocks | WARNING |
| `csharp-perf-001` | N+1 in Entity Framework (lazy loading) | WARNING |

---

### Phase 3: PHP (3–4 days) — Priority 3

**Files:**
- `.semgrep/theloop-rules.yml` → add 10 PHP rules
- `apps/api/alembic/versions/018_add_php_rules.py`
- `tests/test-data/bad/php/*.php`
- `tests/test-data/good/php/*.php`

**Rules (10):**

| ID | Detects | Severity |
|---|---|---|
| `php-injection-001` | SQL via string concat (mysqli/PDO) | ERROR |
| `php-injection-002` | Command injection (shell_exec, exec) | ERROR |
| `php-injection-003` | Path traversal via $_GET/$_POST | ERROR |
| `php-input-001` | $_GET/$_POST used without sanitize | WARNING |
| `php-crypto-001` | md5/sha1 for password hashing | ERROR |
| `php-crypto-002` | Insecure random (rand, mt_rand) | WARNING |
| `php-security-001` | Hardcoded DB credentials | ERROR |
| `php-security-002` | extract() with user input | ERROR |
| `php-security-003` | eval() anywhere | ERROR |
| `php-perf-001` | In-loop DB queries | WARNING |

---

### Phase 4: Ruby (3 days) — Priority 4

**Files:**
- `.semgrep/theloop-rules.yml` → add 10 Ruby rules
- `apps/api/alembic/versions/019_add_ruby_rules.py`
- `tests/test-data/bad/ruby/*.rb`
- `tests/test-data/good/ruby/*.rb`

**Rules (10):**

| ID | Detects | Severity |
|---|---|---|
| `ruby-injection-001` | SQL via string interpolation (ActiveRecord) | ERROR |
| `ruby-injection-002` | Command injection (system, backticks) | ERROR |
| `ruby-input-001` | params used without permit/sanitize | WARNING |
| `ruby-crypto-001` | Insecure random (rand, SecureRandom not used) | WARNING |
| `ruby-crypto-002` | bcrypt not used for passwords | ERROR |
| `ruby-security-001` | Hardcoded secrets in code | ERROR |
| `ruby-security-002` | eval/instance_eval anywhere | ERROR |
| `ruby-rails-001` | CSRF protection disabled | WARNING |
| `ruby-rails-002` | Sensitive data in logs | WARNING |
| `ruby-perf-001` | N+1 queries (includes not used) | WARNING |

---

### Phase 5: Kotlin (3–4 days) — Priority 5

**Files:**
- `.semgrep/theloop-rules.yml` → add 10 Kotlin rules
- `apps/api/alembic/versions/020_add_kotlin_rules.py`
- `tests/test-data/bad/kotlin/*.kt`
- `tests/test-data/good/kotlin/*.kt`

**Rules (10):**

| ID | Detects | Severity |
|---|---|---|
| `kotlin-injection-001` | SQL injection (similar to Java) | ERROR |
| `kotlin-coroutine-001` | GlobalScope.launch (non-cancellable) | WARNING |
| `kotlin-coroutine-002` | launch without proper error handling | WARNING |
| `kotlin-crypto-001` | Weak hash algorithms | WARNING |
| `kotlin-crypto-002` | Random for secrets | WARNING |
| `kotlin-security-001` | TLS verification disabled | ERROR |
| `kotlin-security-002` | Hardcoded credentials | ERROR |
| `kotlin-security-003` | Unsafe deserialization | ERROR |
| `kotlin-null-001` | !! operator overuse (non-null assertion) | WARNING |
| `kotlin-perf-001` | N+1 in DB loops | WARNING |

---

### Phase 6: Rust (2–3 days) — Priority 6

**Files:**
- `.semgrep/theloop-rules.yml` → add 8 Rust rules
- `apps/api/alembic/versions/021_add_rust_rules.py`
- `tests/test-data/bad/rust/src/lib.rs` + `src/main.rs`
- `tests/test-data/good/rust/src/lib.rs` + `src/main.rs`

**Rules (8):**

| ID | Detects | Severity |
|---|---|---|
| `rust-unsafe-001` | Unsafe block without comment/justification | WARNING |
| `rust-unsafe-002` | Unsafe dereference without bounds check | ERROR |
| `rust-crypto-001` | Weak hash (md5, sha1) | WARNING |
| `rust-crypto-002` | Insecure random (rand without proper seed) | WARNING |
| `rust-security-001` | TLS verification disabled | ERROR |
| `rust-library-panic-001` | panic! in library code (non-main) | ERROR |
| `rust-sql-001` | SQL via string concat (sqlx without macro) | ERROR |
| `rust-unwrap-001` | unwrap() in production code (Result/Option) | WARNING |

---

### Phase 7: C/C++ (4–5 days) — Priority 7

**Files:**
- `.semgrep/theloop-rules.yml` → add 10 C/C++ rules
- `apps/api/alembic/versions/022_add_cpp_rules.py`
- `tests/test-data/bad/cpp/*.cpp` + `*.h`
- `tests/test-data/good/cpp/*.cpp` + `*.h`

**Rules (10):**

| ID | Detects | Severity |
|---|---|---|
| `cpp-buffer-001` | strcpy/sprintf without bounds | ERROR |
| `cpp-buffer-002` | gets() used | ERROR |
| `cpp-format-001` | printf with user input as format string | ERROR |
| `cpp-crypto-001` | Custom crypto implementation (not OpenSSL) | ERROR |
| `cpp-memory-001` | malloc without null check | WARNING |
| `cpp-memory-002` | Memory leak (malloc without free) | WARNING |
| `cpp-security-001` | Hardcoded credentials | ERROR |
| `cpp-sql-001` | SQL injection (string concat) | ERROR |
| `cpp-ssl-001` | OpenSSL without peer verification | ERROR |
| `cpp-input-001` | User input to system() or exec | ERROR |

---

## Deliverables per Language

For each of the 7 languages:

1. **Semgrep Rules**
   - 8–15 rules added to `.semgrep/theloop-rules.yml`
   - Each rule: proper language syntax, CWE mapping, severity
   - `semgrep --validate` passes

2. **Test Data** (`tests/test-data/bad/<lang>/` and `good/<lang>/`)
   - 5–8 files demonstrating violations (bad/)
   - 2–3 files showing compliant patterns (good/)
   - Each file tests 1–2 rules, minimal noise

3. **Migration**
   - New `0{16-22}_add_<lang>_rules.py` migration
   - Loads rules into DB, idempotent
   - Validates before insert
   - `connection.commit()` after successful update

4. **Validation**
   - `semgrep --validate --config .semgrep/theloop-rules.yml` → all rules pass
   - `pytest tests/test-data/bad/<lang>/` → rules fire on all bad files
   - `pytest tests/test-data/good/<lang>/` → no false positives on good files

5. **CI / Docs**
   - Update `.semgrep/theloop-rules.yml.bak` (fallback)
   - Update `CLAUDE.md` with language-specific patterns (if needed)
   - All tests pass, coverage ≥ 80%

---

## Architecture: Rule Template

All rules follow the same template for consistency:

```yaml
- id: <lang>-<category>-<number>
  languages: [<lang>]
  message: "[The Loop] <description>"
  severity: ERROR | WARNING
  metadata:
    category: <injection|crypto|security|performance|error|lang-specific>
    cwe: "CWE-XXX"
  patterns:
    - pattern-either:
        - pattern: <pattern1>
        - pattern: <pattern2>
    - pattern-not: <safe_variant>
```

**Example (Java SQL injection):**

```yaml
- id: java-injection-001
  languages: [java]
  message: "[The Loop] SQL injection via string concatenation"
  severity: ERROR
  metadata:
    category: injection
    cwe: "CWE-89"
  patterns:
    - pattern-either:
        - pattern: $STMT.executeQuery("..." + $INPUT)
        - pattern: $STMT.executeUpdate($QUERY + $INPUT)
```

---

## Estimation

| Phase | Language | Days | Rules | Status |
|-------|----------|------|-------|--------|
| 1 | Java | 5–6 | 15 | Pending |
| 2 | C# | 5–6 | 15 | Pending |
| 3 | PHP | 3–4 | 10 | Pending |
| 4 | Ruby | 3 | 10 | Pending |
| 5 | Kotlin | 3–4 | 10 | Pending |
| 6 | Rust | 2–3 | 8 | Pending |
| 7 | C/C++ | 4–5 | 10 | Pending |
| – | **TOTAL** | **~30–35** | **~78** | – |

**Buffer:** 3–5 days for reviews, testing, CI issues, Semgrep pattern refinement.

---

## Verification

### Pre-Merge Checklist (per Phase)

- [ ] `semgrep --validate --config .semgrep/theloop-rules.yml` → 0 errors, N rules
- [ ] All bad test files trigger rules: `semgrep scan tests/test-data/bad/<lang>/`
- [ ] No false positives in good files: `semgrep scan tests/test-data/good/<lang>/` (0 findings)
- [ ] Migration idempotent: re-run produces no errors
- [ ] Ruff + mypy + pytest pass
- [ ] Coverage ≥ 80%
- [ ] CI green (all gates pass)

### Post-Merge Verification

For each language phase:
1. Merge to `main`
2. Cloud Run deployment auto-triggers
3. Verify: `curl https://api.loop.oute.pro/api/v1/rules/latest | jq '.rules_count'` → incremented
4. Verify: `https://loop.oute.pro/rules/` displays new rules
5. Verify: GitHub Actions workflow next scan picks up new rules

### Final Verification (All 7 Phases Complete)

- [ ] Total rules: 123 (45 legacy + 78 new)
- [ ] All languages covered: Java, C#, PHP, Ruby, Kotlin, Rust, C/C++
- [ ] `.semgrep/theloop-rules.yml.bak` in sync
- [ ] All 7 migrations merged
- [ ] Public rule browser shows all languages
- [ ] No CI failures across the board

---

## Out of Scope

- **Swift, Scala, Dart** → Phase 8 (future)
- **Custom rules per project** → Spec-018
- **AI-suggested rules** → Spec-019
- **Rule whitelisting by team** → Spec-020
- **Remediation suggestions** → Phase C (future)

---

## Branch Strategy

```
main (123 total rules after completion)
  ├── feat/017-java (merge → rebase)
  ├── feat/017-csharp
  ├── feat/017-php
  ├── feat/017-ruby
  ├── feat/017-kotlin
  ├── feat/017-rust
  └── feat/017-cpp
```

**Branching approach:**
- Create feature branch per language
- Each branch self-contained (rules YAML + migration + tests)
- Sequential merges (no parallel branches to same YAML)
- Rebase + merge to avoid merge commits

---

## Files Modified / Created

| File | Change |
|---|---|
| `.semgrep/theloop-rules.yml` | Add ~78 rules across 7 languages |
| `.semgrep/theloop-rules.yml.bak` | Sync after each phase |
| `apps/api/alembic/versions/016-022_*.py` | 7 migrations (one per language) |
| `tests/test-data/bad/<lang>/*.{java,cs,php,rb,kt,rs,cpp}` | ~50 bad example files |
| `tests/test-data/good/<lang>/*.{java,cs,php,rb,kt,rs,cpp}` | ~15 good example files |
| `CLAUDE.md` | Document language-specific patterns (optional) |

---

## Related Docs

- **Spec-016:** Rules foundation (Python, JS/TS, Go) — see `specs/016-semgrep-platform/spec.md`
- **Spec-015:** UI/Navigation (Dashboard, Profile) — see `specs/015-*/spec.md`
- **.semgrep/theloop-rules.yml:** Current 45 rules, v0.3.0
- **Semgrep Docs:** https://semgrep.dev/docs/writing-rules/

---

## Success Criteria

✅ **Spec-017 is complete when:**

1. All 7 languages have 8–15 rules each (~78 total)
2. All rules validated: `semgrep --validate` passes
3. All test data (bad/ + good/) passes locally
4. All 7 migrations merged + deployed
5. Public rule browser (`/rules/`) displays all 123 rules
6. No CI failures
7. Coverage ≥ 80%
