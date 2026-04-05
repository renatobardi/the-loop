# Phase 1: Data Model

**Date**: 2026-04-05  
**Feature**: Multi-Language Rules Expansion (Spec-018)

---

## Core Entities

### Entity 1: Semgrep Rule

**Purpose**: Immutable definition of a single security pattern to be detected.

**Fields**:

| Field | Type | Constraints | Example |
|-------|------|-------------|---------|
| `id` | string | Unique, kebab-case, max 50 chars | `java-injection-001` |
| `languages` | list[string] | Non-empty, valid language codes | `["java"]` or `["c", "cpp"]` |
| `message` | string | Descriptive, max 200 chars, must start with "[The Loop]" | `"[The Loop] SQL injection via string concatenation"` |
| `severity` | enum | Must be `ERROR` or `WARNING` | `ERROR` |
| `patterns` | list[object] | Non-empty, valid Semgrep patterns | `[{"pattern": "$STMT.executeQuery($Q + $I)"}]` |
| `metadata` | object | Must contain `category` (string) and optional `cwe` (string) | `{"category": "injection", "cwe": "CWE-89"}` |

**Validation Rules**:

- `id` format: `{language}-{category}-{number}` (e.g., `java-injection-001`)
- `languages` must match Semgrep's official language list (Python, JavaScript, TypeScript, Java, Go, C#, PHP, Ruby, Kotlin, Rust, C, C++)
- `severity` values only: `ERROR` (blocks merge in CI) or `WARNING` (advisory)
- `metadata.category` must be one of: `injection`, `crypto`, `security`, `performance`, `error-handling`, `lang-specific`
- `metadata.cwe` format: `CWE-{number}` (e.g., `CWE-89`)

**Relationships**:

- Many-to-One: Rule → Language (each rule targets 1+ languages)
- Many-to-One: Rule → Category (via metadata)
- Many-to-One: Rule → CWE (via metadata)

**Immutability**: Once created and merged, a rule's ID and patterns MUST NOT change (immutable by convention). Updates require new rule ID + deprecation of old rule.

---

### Entity 2: Rule Version

**Purpose**: A cohesive set of rules published together, representing a version of The Loop's security platform.

**Fields** (database `rule_versions` table):

| Field | Type | Constraints | Example |
|-------|------|-------------|---------|
| `id` | UUID | Primary key | `550e8400-e29b-41d4-a716-446655440000` |
| `version` | string | Unique, semantic versioning | `v0.4.0` |
| `rules_json` | JSON | Non-null, valid JSON array of Rule objects | `[{rule1}, {rule2}, ...]` |
| `status` | enum | `active`, `deprecated`, or `draft` | `active` |
| `created_at` | timestamp | Immutable, UTC | `2026-04-05T12:00:00Z` |
| `published_by` | UUID | Foreign key to `users.id` | `550e8400-...` |
| `notes` | text | Optional release notes | `"Phase 7: C/C++ rules"` |
| `deprecated_at` | timestamp | Null unless status=deprecated | `2026-06-01T12:00:00Z` |

**Validation Rules**:

- `version` must follow semantic versioning (v{major}.{minor}.{patch})
- `rules_json` is a JSON array of Rule objects; must validate each rule before insertion
- `status` transitions: `draft` → `active` (publish), `active` → `deprecated` (deprecate); no reverse
- `created_at` is set at insertion; never modified
- Only one `active` version per release cycle (convention; not enforced at DB level)

**Relationships**:

- One-to-Many: RuleVersion → Rules (rules_json contains array)
- One-to-One: RuleVersion → User (published_by)

---

### Entity 3: Language Phase

**Purpose**: Logical grouping of 8–15 rules for one target language, deployed atomically.

**Composition**:

| Component | Type | Contains |
|-----------|------|----------|
| Rules | list | 8–15 Rule objects for target language |
| Test data | directory | `tests/test-data/bad/{lang}/` (5–8 files) + `good/{lang}/` (2–3 files) |
| Migration | Python file | Alembic migration (e.g., `016_add_java_rules.py`) |

**Lifecycle**:

1. **Created**: Rules defined, test data written, migration generated
2. **Validated**: `semgrep --validate` passes, bad files trigger rules, good files produce 0 FP
3. **Committed**: Code reviewed, pushed to branch
4. **Merged**: PR merged to main
5. **Deployed**: Migration auto-runs on Cloud Run; rules live in API and web UI
6. **Monitored**: Check API response, web UI display, false-positive reports from CI scans

**Idempotency**: Each migration can be re-run without error (guard clause detects existing rules and skips).

---

### Entity 4: Rule Category

**Purpose**: Taxonomy grouping vulnerabilities by attack vector.

**Values**:

| Category | Vulnerability Types | Example CWE |
|----------|---------------------|-------------|
| `injection` | SQL injection, command injection, path traversal, XXE | 89, 78, 22, 611 |
| `crypto` | Weak hashes, weak random, hardcoded secrets | 327, 338, 798 |
| `security` | TLS disabled, CORS wildcard, unsafe deserialization | 295, 345, 502 |
| `performance` | N+1 queries, unbounded loops, missing timeouts | Custom |
| `error-handling` | Silently caught exceptions, panics in handlers | Custom |
| `lang-specific` | Language quirks (e.g., unsafe Rust, JDBC in Java) | Varies |

**Cardinality**: Many-to-One (each rule maps to exactly one category via `metadata.category`).

---

## State Transitions

### Rule Version States

```
                ┌─────────────────────────────────┐
                │  [draft]  (published but hidden)  │
                │  created at version date          │
                │  status = "draft"                 │
                └──────────┬──────────────────────┘
                           │
                           │ publish()
                           │ (status → "active")
                           ▼
                ┌─────────────────────────────────┐
                │  [active] (live to users)         │
                │  published_by = user UUID         │
                │  status = "active"                │
                │  /rules/latest returns this       │
                └──────────┬──────────────────────┘
                           │
                           │ deprecate()
                           │ (status → "deprecated",
                           │  deprecated_at = now)
                           ▼
                ┌─────────────────────────────────┐
                │  [deprecated] (archived)          │
                │  deprecated_at = timestamp        │
                │  status = "deprecated"            │
                │  /rules/deprecated returns this   │
                └─────────────────────────────────┘
```

**Transitions Allowed**:
- draft → active (via publish)
- active → deprecated (via deprecate)
- No reverse transitions (immutable history)

---

## Constraints & Validation

### Rule-Level Validation

```python
class Rule:
    id: str  # matches {lang}-{category}-{num}
    languages: list[str]  # non-empty, valid codes
    message: str  # starts with "[The Loop]", < 200 chars
    severity: Literal["ERROR", "WARNING"]
    patterns: list[dict]  # non-empty, valid Semgrep syntax
    metadata: dict  # must have category, optional cwe
```

### Version-Level Validation

```python
class RuleVersion:
    version: str  # semantic versioning
    rules_json: list[Rule]  # each rule validates
    status: Literal["draft", "active", "deprecated"]
    created_at: datetime  # UTC
    published_by: UUID
    notes: Optional[str]
    deprecated_at: Optional[datetime]  # null if not deprecated
```

### Invariants

- **No duplicate rule IDs**: Within a version, each rule.id is unique
- **Language consistency**: All rules in a phase target the same language (e.g., `languages: ["java"]`)
- **Immutable ID**: Once a rule is published (version status = active), its ID MUST NOT change
- **Single active version per language**: At most one RuleVersion has status=active (convention, enforced by application logic)

---

## References

- **Spec**: [spec.md](spec.md)
- **API Response Example**: [contracts/rule-schema.md](contracts/rule-schema.md)
- **Database Schema**: [apps/api/src/adapters/postgres/models.py](../../apps/api/src/adapters/postgres/models.py) (existing RuleVersionRow)
