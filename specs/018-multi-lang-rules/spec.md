# Feature Specification: Multi-Language Rules Expansion

**Feature Branch**: `018-multi-lang-rules`  
**Created**: 2026-04-05  
**Status**: Draft  
**Input**: Expand Semgrep rules to 7 additional languages (Java, C#, PHP, Ruby, Kotlin, Rust, C/C++) with ~78 rules total, following Phase A-C pattern taxonomy

---

## Context

The Loop currently distributes 45 security rules across Python (20), JavaScript/TypeScript (15), and Go (10) as of Spec-016 completion. This specification extends coverage to 7 additional languages representing the top 10 most-used programming languages globally. The result is a language-agnostic security platform that detects incident patterns across diverse development ecosystems.

**Target Users**:
- Development teams using Java, C#, PHP, Ruby, Kotlin, Rust, or C/C++
- CI/CD pipelines scanning repositories in these languages
- Security teams needing consistent vulnerability detection across polyglot codebases

---

## User Scenarios & Testing

### User Story 1 - Java Development Team Detects SQL Injection Vulnerabilities (Priority: P1)

A Java development team uses The Loop in their CI/CD pipeline to scan for security violations during pull requests. They benefit from 15 Java-specific rules that catch common patterns like SQL injection via string concatenation, unsafe JDBC usage, and hardcoded credentials.

**Why this priority**: Java is the 3rd most-used language globally. SQL injection and hardcoded credentials are the #1 and #2 security issues in Java codebases. Immediate value to largest Java user base.

**Independent Test**: Can be fully tested by running `semgrep scan` with Java rules on a sample repository with known violations, validating all bad patterns trigger and good patterns pass.

**Acceptance Scenarios**:

1. **Given** a Java file with SQL concatenation `statement.executeQuery("SELECT * FROM users WHERE id=" + userId)`, **When** Semgrep scans it, **Then** rule `java-injection-001` fires with ERROR severity
2. **Given** a Java file with proper PreparedStatement usage, **When** Semgrep scans it, **Then** no java-injection rules fire
3. **Given** a Java file with hardcoded API credentials `private static final String API_KEY = "sk-1234567..."`, **When** Semgrep scans it, **Then** rule `java-security-002` fires with ERROR severity

---

### User Story 2 - C# Team Ensures LINQ Injection Prevention (Priority: P1)

A C# development team scanning Entity Framework and LINQ queries detects dynamic query injection patterns that could allow attackers to modify SQL at runtime. They deploy with confidence knowing parameterized queries are enforced.

**Why this priority**: C# ranks in top 10 languages. LINQ injection is a critical vulnerability in .NET applications. High business impact for enterprises using C#.

**Independent Test**: Validate that `csharp-linq-001` fires on dynamic expression trees and `csharp-sql-001` fires on non-parameterized SqlCommand queries. Verify no false positives on parameterized queries.

**Acceptance Scenarios**:

1. **Given** a C# file with `new SqlCommand("SELECT * FROM users WHERE id=" + id)`, **When** Semgrep scans it, **Then** rule `csharp-sql-001` fires
2. **Given** a C# file with LINQ `context.Users.FromSqlInterpolated($"SELECT * FROM users WHERE id={id}")`, **When** Semgrep scans it, **Then** rule `csharp-linq-001` fires

---

### User Story 3 - PHP Application Prevents Command Injection (Priority: P2)

A PHP web application team uses The Loop to scan for shell_exec, exec, and system() calls with unsanitized user input. Rules prevent attackers from executing arbitrary OS commands.

**Why this priority**: PHP is widely used in web applications. Command injection via $_GET/$_POST is a common vulnerability. P2 because smaller active PHP community than Java/C#.

**Independent Test**: Verify `php-injection-002` fires on `shell_exec($_GET['cmd'])` and `php-input-001` warns on unsanitized $_POST usage.

**Acceptance Scenarios**:

1. **Given** a PHP file with `exec($_GET['command'])`, **When** Semgrep scans it, **Then** rule `php-injection-002` fires with ERROR severity

---

### User Story 4 - Ruby/Rails Team Prevents N+1 Queries (Priority: P2)

A Rails development team detects N+1 query patterns where database queries are executed inside loops, causing performance degradation. The rule `ruby-perf-001` ensures `.includes()` is used for associations.

**Why this priority**: Ruby on Rails is a strong ecosystem but smaller community. Performance issues are detectable but not security-critical. P2 is appropriate.

**Independent Test**: Validate rule fires on `for user in users; user.posts.all; end` and passes on `User.includes(:posts).all`.

**Acceptance Scenarios**:

1. **Given** a Rails controller iterating users without eager loading, **When** Semgrep scans it, **Then** rule `ruby-perf-001` warns

---

### User Story 5 - Kotlin/Coroutine Team Prevents Non-Cancellable Scope Usage (Priority: P3)

A Kotlin team scans for `GlobalScope.launch()` usage, which creates non-cancellable coroutines that leak memory and are hard to test. Rule `kotlin-coroutine-001` enforces proper scope management.

**Why this priority**: Kotlin is growing but has smaller user base. Coroutine misuse is a code quality issue, not critical security. Valuable for Kotlin ecosystem but lower priority.

**Independent Test**: Verify rule fires on `GlobalScope.launch { ... }` and passes on `lifecycleScope.launch { ... }`.

**Acceptance Scenarios**:

1. **Given** a Kotlin file with `GlobalScope.launch()`, **When** Semgrep scans it, **Then** rule `kotlin-coroutine-001` fires with WARNING severity

---

### User Story 6 - Rust Library Author Prevents Unsafe Dereference (Priority: P3)

A Rust library author ensures unsafe blocks are justified and memory is properly managed. Rules like `rust-unsafe-001` and `rust-unwrap-001` catch risky patterns in production code.

**Why this priority**: Rust has growing adoption but smaller active codebase. Unsafe memory is important but Rust's compiler catches most issues. Good to have but lower priority than Java/C#.

**Independent Test**: Verify `rust-unsafe-001` warns on uncommented unsafe blocks and `rust-unwrap-001` warns on unwrap() in non-main code.

**Acceptance Scenarios**:

1. **Given** a Rust library file with `unsafe { ... }` without justifying comment, **When** Semgrep scans it, **Then** rule `rust-unsafe-001` fires with WARNING

---

### User Story 7 - C/C++ Team Prevents Buffer Overflow (Priority: P3)

A C/C++ embedded systems team detects buffer overflow vulnerabilities like `strcpy()` and `gets()` that are known to cause security breaches. Rules catch unsafe string operations.

**Why this priority**: C/C++ is essential for systems programming but has smallest active web development community. Buffer overflows are critical but harder to express in Semgrep patterns. P3 reflects lower community size.

**Independent Test**: Verify `cpp-buffer-001` fires on `strcpy(dest, src)` without bounds checking.

**Acceptance Scenarios**:

1. **Given** a C file with `strcpy(buffer, input)`, **When** Semgrep scans it, **Then** rule `cpp-buffer-001` fires with ERROR severity

---

### Edge Cases

- What happens when a language has multiple syntax variants (e.g., Ruby with and without `.call()` syntax for Procs)? → Rules should match common patterns; edge cases handled via `pattern-not` excludes
- How does the system handle rules that apply to both application code and library code? → Some rules fire on both; library-specific rules (e.g., `rust-library-panic-001`) only for non-main code
- What if a rule matches across language boundaries (e.g., hardcoded credentials in YAML config files)? → Rules are language-specific; generic patterns handled in existing "generic" category
- What if a new version of a language (e.g., C++20) introduces new unsafe patterns? → Rules are written for common idioms; language version specifics handled in metadata
- What if a rule has high false-positive rate on real-world code? → Validation phase (Phase 7) runs against test data; false positives refined before production merge

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST include 8–15 Semgrep rules for each of 7 languages (Java, C#, PHP, Ruby, Kotlin, Rust, C/C++)
- **FR-002**: System MUST validate all rules via `semgrep --validate` with 0 errors
- **FR-003**: System MUST categorize rules into Injection, Cryptography, Security, Performance, Error Handling, and Language-Specific groups
- **FR-004**: System MUST attach CWE (Common Weakness Enumeration) identifiers to security-relevant rules
- **FR-005**: System MUST assign severity levels (ERROR for critical, WARNING for advisory) based on risk profile
- **FR-006**: System MUST provide test data (bad/ and good/ examples) for each language demonstrating rule coverage
- **FR-007**: System MUST support idempotent database migrations for each language phase (one migration per language)
- **FR-008**: System MUST update `.semgrep/theloop-rules.yml.bak` fallback file after each language phase completes
- **FR-009**: System MUST publish rules to public API endpoint `/api/v1/rules/latest` with incremented `rules_count`
- **FR-010**: System MUST display all rules on public web interface at `/rules/` without authentication

### Key Entities

- **Semgrep Rule**: Represents a single pattern-matching security rule with id, languages, message, severity, patterns, metadata
- **Language Phase**: A cohesive set of rules for one language (8–15 rules), deployed as a single Alembic migration
- **Rule Category**: Taxonomy (Injection, Crypto, Security, etc.) organizing rules by attack vector
- **Migration**: Database operation to persist rules in `rule_versions` table, versioned incrementally (016–022)

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 7 languages have rules deployed: Java (15), C# (15), PHP (10), Ruby (10), Kotlin (10), Rust (8), C/C++ (10) = 78 total rules
- **SC-002**: `semgrep --validate --config .semgrep/theloop-rules.yml` passes with 0 errors across all 123 rules (45 existing + 78 new)
- **SC-003**: 100% of bad test files (5–8 per language) trigger at least one rule; 100% of good test files (2–3 per language) produce 0 false positives
- **SC-004**: All 7 Alembic migrations (016–022) are idempotent and can be re-run without error
- **SC-005**: Public rule browser at `/rules/` displays all 123 rules grouped by language and severity
- **SC-006**: CI/CD pipeline passes all gates (ruff, mypy, pytest ≥ 80%, Trivy) after each language phase merge
- **SC-007**: Database query `SELECT COUNT(*) FROM rule_versions WHERE version = 'v0.4.0'` returns 1 row after Phase 7 completes
- **SC-008**: Developers can identify which rules apply to their codebase within 30 seconds by browsing `/rules/`

---

## Assumptions

- Each language has 8–15 rules; exact count determined during Phase execution
- Rules follow existing Phase A–C pattern taxonomy (Injection, Crypto, Security, Performance, Error Handling, Language-Specific)
- Existing Semgrep rule syntax and `.yml` format remain unchanged; new rules are additive only
- Test data (bad/ and good/ examples) use file size under 1KB each to keep repository size minimal
- Existing authentication system, CI/CD infrastructure, and database schema require no modifications
- Each phase is independently deployable; subsequent phases do not block prior phases
- Rules are written to match common idioms, not edge cases; false-positive rates acceptable if <5% on production codebases
- C/C++ rules focus on portable, widely-used patterns (e.g., libc string functions) rather than platform-specific vectors
- Swift, Scala, and Dart are out of scope; these languages are Phase 8 candidates
- Custom rule whitelisting per project is out of scope; consumed in Spec-018+

---
