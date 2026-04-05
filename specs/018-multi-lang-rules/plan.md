# Implementation Plan: Multi-Language Rules Expansion

**Branch**: `018-multi-lang-rules` | **Date**: 2026-04-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/018-multi-lang-rules/spec.md`

---

## Summary

Expand Semgrep rule distribution from 45 rules (3 languages: Python, JS/TS, Go) to 123 rules (10 languages) by adding ~78 new rules across 7 additional languages (Java, C#, PHP, Ruby, Kotlin, Rust, C/C++) over 7 sequential phases (30–35 days total). Each language phase delivers rules + test data + database migration, published to public API and web UI. This makes The Loop language-agnostic and covers the global top 10 programming languages.

**Why**: Java, C#, PHP, Ruby, Kotlin, Rust, and C/C++ represent 60%+ of enterprise codebases. Current 45-rule coverage only serves Python, JS/TS, Go developers. Expansion unlocks value for polyglot teams and CI/CD pipelines scanning mixed-language repositories.

---

## Technical Context

**Language/Version**: Python 3.12, Semgrep 1.157.0+, PostgreSQL 16, FastAPI 0.128.5  
**Primary Dependencies**: Semgrep CLI (rule validation), Alembic (schema migrations), pytest (test data validation), ruff + mypy (code quality)  
**Storage**: PostgreSQL `rule_versions` table (existing, no schema change required; rules stored as JSON in `rules_json` column)  
**Testing**: pytest for test data validation, `semgrep --validate` for rule syntax, manual scanning of bad/good examples  
**Target Platform**: Cloud Run (API), public web UI (`/rules/`)  
**Project Type**: Backend service + API expansion (no frontend changes except dashboard link already added)  
**Performance Goals**: Rule validation (<5s per language phase), API response <200ms for `/rules/latest`  
**Constraints**: Zero schema changes to existing tables; migrations must be idempotent; no breaking changes to API contract  
**Scale/Scope**: 78 new rules, 7 language phases, 1 phase per 4–6 days sequential execution

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Relevant Mandamentos**:

- **XIII. Dependencias no Plano de Execucao**: All dependencies MUST be explicit in plan
- **VI. Sem Ambiente de Dev**: Single environment (production); code merged → deployed
- **VII. CI Rigoroso**: All gates must pass (lint, type-check, test, build, security, docs)
- **IX. Clean Code**: Single responsibility per file/function, DRY pragmatic, zero dead code
- **X. Arquitetura Hexagonal**: From Phase 1 onward; this is Phase 3+ of product → applies

**Compliance Review**:

✅ **Mandamento XIII**: All dependencies identified:
- **Infra**: None new (uses existing Cloud Run, PostgreSQL, API, Cloud SQL Proxy)
- **APIs**: None external (internal Semgrep CLI, internal rule publication)
- **CI/CD**: No new jobs; existing CI gates (ruff, mypy, pytest ≥80%, Trivy, docs-check) cover this feature
- **Secrets**: None new (existing Firebase, GCP Secret Manager)
- **Database**: Existing `rule_versions` table; new migrations (016–022) insert into existing table; no schema changes

✅ **Mandamento VI**: Single environment model supported:
- Rules merged → deployed to Cloud Run immediately
- Public API (`/rules/latest`) live in seconds
- No staging; rollback via prior migration version if needed

✅ **Mandamento VII**: CI gates covered:
- `ruff check` on `.semgrep/theloop-rules.yml.bak` (YAML syntax validation)
- `pytest --cov=src --cov-fail-under=80` (test data validation)
- `semgrep --validate` (rule syntax validation) — existing CI job
- `trivy scan` on Docker build (existing security gate)

✅ **Mandamento IX**: Clean Code principles:
- Each language phase = one file (`.semgrep/theloop-rules.yml`), one migration module (e.g., `016_add_java_rules.py`)
- Each rule: single responsibility (detects one pattern family)
- No dead code; no commented-out rules
- Tests follow BDD Given/When/Then format

✅ **Mandamento X**: Hexagonal architecture:
- **Domain**: Rule definitions (pure data; no dependencies)
- **Ports**: `RuleVersionRepository` (exists; no change)
- **Adapters**: `RuleVersionRepository` implementation (unchanged); Alembic migration layer (new, but follows existing pattern)
- **Boundaries**: Semgrep rule syntax ↔ JSON serialization (1:1 mapping, trivial abstraction)

**Gate Status**: ✅ PASS — no mandamento violations. Feature complies with constitution.

---

## Project Structure

### Documentation (this feature)

```text
specs/018-multi-lang-rules/
├── spec.md                          # Feature specification (complete)
├── checklists/
│   └── requirements.md              # Quality checklist (complete)
├── plan.md                          # This file (complete)
├── research.md                      # Phase 0 output (✅ complete)
├── data-model.md                    # Phase 1 output (✅ complete)
├── contracts/
│   └── rule-schema.md               # Phase 1 output (✅ complete)
├── quickstart.md                    # Phase 1 output (optional — design doc only)
└── tasks.md                         # Phase 2 output (✅ complete — created by /speckit.tasks)
```

### Source Code (repository root)

```text
.semgrep/
├── theloop-rules.yml                # Main rules file (updated per phase)
├── theloop-rules.yml.bak            # Fallback for CI (synced per phase)
└── scripts/
    └── json_to_semgrep_yaml.py      # Conversion utility (existing)

apps/api/
├── alembic/versions/
│   ├── 016_add_java_rules.py        # Phase 1 migration (to create)
│   ├── 017_add_csharp_rules.py      # Phase 2 migration (to create)
│   ├── 018_add_php_rules.py         # Phase 3 migration (to create)
│   ├── 019_add_ruby_rules.py        # Phase 4 migration (to create)
│   ├── 020_add_kotlin_rules.py      # Phase 5 migration (to create)
│   ├── 021_add_rust_rules.py        # Phase 6 migration (to create)
│   └── 022_add_cpp_rules.py         # Phase 7 migration (to create)
├── tests/
│   └── test-data/
│       ├── bad/
│       │   ├── java/                # 5–8 violation examples
│       │   ├── csharp/              # 5–8 violation examples
│       │   ├── php/                 # 4–5 violation examples
│       │   ├── ruby/                # 4–5 violation examples
│       │   ├── kotlin/              # 4–5 violation examples
│       │   ├── rust/                # 3–4 violation examples
│       │   └── cpp/                 # 4–5 violation examples
│       └── good/
│           ├── java/                # 2–3 compliant examples
│           ├── csharp/              # 2–3 compliant examples
│           ├── php/                 # 2–3 compliant examples
│           ├── ruby/                # 2–3 compliant examples
│           ├── kotlin/              # 2–3 compliant examples
│           ├── rust/                # 2–3 compliant examples
│           └── cpp/                 # 2–3 compliant examples
└── src/
    └── api/routes/
        └── rules.py                 # Existing (no changes)
```

**Structure Decision**: Linear, single-file rules accumulation. Each language phase updates `.semgrep/theloop-rules.yml` (append-only), creates one Alembic migration, and adds test data. No new source files required; existing API, web UI, and cache layers consume rules without modification.

---

## Complexity Tracking

> **No Constitution Check violations to justify.** This section is empty per Mandamento XVI.

---

## Phase 0: Outline & Research

### Unknowns to Resolve

No [NEEDS CLARIFICATION] markers from spec. However, research tasks to validate best practices:

1. **Semgrep pattern coverage by language**: Ensure `semgrep --validate` accepts all 7 languages without errors
2. **False-positive rates**: Validate test data against production patterns; acceptable threshold <5% FP rate
3. **Rule count distribution**: Confirm 8–15 rules/language is feasible; identify which CWE mappings apply per language
4. **Migration idempotency**: Verify each migration can be re-run safely without corrupting `rule_versions` data

### Research Tasks

**Task R-001**: Validate Semgrep language support
- Research: Which of the 7 languages does Semgrep 1.157.0 officially support?
- Deliverable: Language support matrix (complete/partial/not-yet)
- Rationale: Ensures rule syntax is valid before creating rules

**Task R-002**: Analyze CWE-to-language mapping
- Research: Which CWEs apply to each language? (e.g., buffer overflow → C/C++, SQL injection → all)
- Deliverable: CWE matrix (rows = languages, cols = CWEs)
- Rationale: Guides rule coverage per language; ensures no critical vulnerabilities missed

**Task R-003**: Validate test data patterns
- Research: Run `semgrep scan` against sample bad code files; measure FP rate
- Deliverable: FP benchmark per language
- Rationale: Confirms rule quality before production merge

### Research Output

**research.md** will document:
- Semgrep language support status (yes/no per language)
- CWE-to-language mapping table
- False-positive benchmark (<5% target)
- Migration idempotency strategy (if-exists guards)

---

## Phase 1: Design & Contracts

### 1.1 Data Model (data-model.md)

**Entities**:

- **Semgrep Rule**: Immutable rule definition
  - Fields: id, languages, message, severity, patterns, metadata (CWE)
  - Validation: id format (kebab-case), languages non-empty, severity in {ERROR, WARNING}
  
- **Language Phase**: Cohesive rule set for one language
  - Contains: 8–15 rules, test data (bad/ + good/), Alembic migration
  - Relationships: 1-to-many rules, 1-to-one migration
  
- **Rule Category**: Taxonomy grouping
  - Values: Injection, Cryptography, Security, Performance, Error Handling, Language-Specific
  - Cardinality: Many-to-one (rule → category)

- **Migration**: Database operation
  - Fields: revision id (016–022), version (e.g., "v0.4.0"), language phase
  - Idempotency: Skip if rule_count ≥ N or rules already exist

### 1.2 Interface Contracts (contracts/)

**Rule Storage Contract** (`rule-schema.md`):

Input (JSON to store):
```json
{
  "id": "java-injection-001",
  "languages": ["java"],
  "message": "[The Loop] SQL injection via string concatenation",
  "severity": "ERROR",
  "metadata": {"cwe": "CWE-89", "category": "injection"},
  "patterns": [{"pattern": "$STMT.executeQuery($QUERY + $INPUT)"}]
}
```

Output (API response):
```json
{
  "version": "v0.4.0",
  "rules_count": 78,
  "rules": [
    {
      "id": "java-injection-001",
      "languages": ["java"],
      "message": "[The Loop] SQL injection via string concatenation",
      "severity": "ERROR",
      "metadata": {"cwe": "CWE-89", "category": "injection"},
      "patterns": [{"pattern": "$STMT.executeQuery($QUERY + $INPUT)"}]
    },
    ...
  ]
}
```

Constraints:
- No schema changes to `rule_versions` table
- JSON stored as-is in `rules_json` column
- API response includes all fields; web UI renders subset (id, message, severity, metadata)

### 1.3 Quick Start (quickstart.md)

1. Create Alembic migration: `alembic revision --autogenerate -m "add_{lang}_rules"`
2. Add rules to `.semgrep/theloop-rules.yml` (append to file, don't delete existing)
3. Add test data: `tests/test-data/bad/{lang}/` (5–8 files), `tests/test-data/good/{lang}/` (2–3 files)
4. Validate: `semgrep --validate --config .semgrep/theloop-rules.yml`
5. Run tests: `pytest tests/test-data/bad/{lang}/` → rules fire; `pytest tests/test-data/good/{lang}/` → 0 findings
6. Migrate: `alembic upgrade head`
7. Sync fallback: `cp .semgrep/theloop-rules.yml .semgrep/theloop-rules.yml.bak`
8. Push → PR → merge → Cloud Run deployment

### 1.4 Agent Context Update

Run: `.specify/scripts/bash/update-agent-context.sh claude`

Updates `/Users/bardi/.claude/projects/-Users-bardi-Projetos-the-loop/memory/MEMORY.md`:
- Add entry: Spec-018 (Rules Expansion) — 7 languages, 78 rules, 30–35 days, migration-per-language pattern
- Note: Uses existing Semgrep infrastructure; no new external APIs

---

## Phase 2: Task Breakdown

**Output**: tasks.md (generated by `/speckit.tasks` command)

Tasks will follow this structure per language phase:
- **Phase {N} — {Language}** ({Days} days, {Priority})
  - T1: Write {N} rules to `.semgrep/theloop-rules.yml`
  - T2: Validate rules via `semgrep --validate`
  - T3: Add test data (bad/ + good/)
  - T4: Create Alembic migration `0{15+N}_add_{lang}_rules.py`
  - T5: Run tests; confirm rules fire on bad, pass on good
  - T6: Migrate database: `alembic upgrade head`
  - T7: Sync fallback: `cp .semgrep/theloop-rules.yml .semgrep/theloop-rules.yml.bak`
  - T8: Push PR; CI validates (ruff, mypy, pytest ≥80%, Trivy)
  - T9: Merge → Cloud Run deployment (automatic)

---

## Success Metrics

- ✅ All 78 rules validated by `semgrep --validate`
- ✅ 100% of bad test files trigger at least one rule
- ✅ 100% of good test files → 0 false positives
- ✅ All 7 migrations idempotent (can re-run without error)
- ✅ Public API `/rules/latest` returns `rules_count: 123` after Phase 7
- ✅ Web UI `/rules/` displays all 123 rules grouped by language + severity
- ✅ CI gates pass (ruff, mypy, pytest ≥80%, Trivy, docs-check)
- ✅ Database transaction test: `SELECT COUNT(*) FROM rule_versions WHERE version IN (...)` returns 7 rows (one per phase)

---

## Open Questions for Phase 0 Research

1. Does Semgrep 1.157.0 officially support all 7 target languages (Java, C#, PHP, Ruby, Kotlin, Rust, C/C++)? → research.md will confirm
2. What is the acceptable false-positive rate for test data? → Assume <5% per language
3. For C/C++, should rules target C99/C11 or C++11+? → Assume both (use `languages: ["c", "cpp"]`)

---

## References

- **Spec**: [spec.md](spec.md)
- **Checklist**: [checklists/requirements.md](checklists/requirements.md)
- **Constitution**: [CONSTITUTION.md](../../CONSTITUTION.md)
- **Existing rules**: [.semgrep/theloop-rules.yml](../../.semgrep/theloop-rules.yml)
- **Migration pattern**: [apps/api/alembic/versions/015_fix_rule_versions_v030_full_rules.py](../../apps/api/alembic/versions/015_fix_rule_versions_v030_full_rules.py)
