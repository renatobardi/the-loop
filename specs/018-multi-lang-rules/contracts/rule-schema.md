# Interface Contract: Rule Storage & Retrieval

**Date**: 2026-04-05  
**Feature**: Multi-Language Rules Expansion (Spec-018)

---

## Rule Storage Format (Database JSON)

Rules are stored in `rule_versions.rules_json` as a JSON array. Each rule follows this schema:

```json
{
  "id": "string (required)",
  "languages": ["string (required, 1+ items)"],
  "message": "string (required, max 200 chars)",
  "severity": "ERROR | WARNING (required)",
  "patterns": [
    {
      "pattern": "string (Semgrep pattern syntax)"
    }
  ],
  "metadata": {
    "category": "string (required, one of: injection|crypto|security|performance|error-handling|lang-specific)",
    "cwe": "string (optional, format: CWE-{number})"
  }
}
```

**Example**:

```json
{
  "id": "java-injection-001",
  "languages": ["java"],
  "message": "[The Loop] SQL injection via string concatenation",
  "severity": "ERROR",
  "patterns": [
    {
      "pattern": "$STMT.executeQuery($QUERY + $INPUT)"
    }
  ],
  "metadata": {
    "category": "injection",
    "cwe": "CWE-89"
  }
}
```

---

## API Response Format

**Endpoint**: `GET /api/v1/rules/latest`  
**Status**: 200 OK | 503 Service Unavailable

**Response Body** (200):

```json
{
  "version": "string (semantic version, e.g., v0.4.0)",
  "rules_count": "integer (count of rules in this version)",
  "rules": [
    {
      "id": "string",
      "languages": ["string"],
      "message": "string",
      "severity": "ERROR | WARNING",
      "patterns": [{"pattern": "string"}],
      "metadata": {
        "category": "string",
        "cwe": "string (optional)"
      }
    }
  ],
  "created_at": "ISO 8601 timestamp",
  "published_by": "string (user UUID)"
}
```

**Response Example** (after Phase 7 completion):

```json
{
  "version": "v0.4.0",
  "rules_count": 123,
  "rules": [
    {
      "id": "injection-001-sql-string-concat",
      "languages": ["python", "javascript", "typescript", "java", "go", "ruby"],
      "message": "[The Loop] SQL injection via string concatenation",
      "severity": "ERROR",
      "patterns": [
        {
          "pattern": "$DB.execute(\"...\" + $INPUT)"
        },
        {
          "pattern": "$DB.execute(f\"...{$INPUT}...\")"
        }
      ],
      "metadata": {
        "category": "injection",
        "cwe": "CWE-89"
      }
    },
    { ... 122 more rules ... }
  ],
  "created_at": "2026-05-15T10:30:00Z",
  "published_by": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Web UI Display Contract

**Endpoint**: `GET /rules/` (public, no auth)  
**Status**: 200 OK | 503 Service Unavailable

**Rendered Output**:

- Page title: "Active Rules" (version from API)
- Cards grouped by **severity**: Critical (ERROR) first, then Warnings (WARNING)
- Each card displays:
  - Rule ID (e.g., `java-injection-001`)
  - Message (e.g., `"[The Loop] SQL injection via string concatenation"`)
  - Languages (badge list: Java, C#, PHP, ...)
  - Severity badge (red = ERROR, yellow = WARNING)
  - Metadata (CWE link if available)

**Example Card**:

```
┌─────────────────────────────────────────────────────────────┐
│ 🔴 ERROR                                                     │
├─────────────────────────────────────────────────────────────┤
│ java-injection-001                                           │
│ [The Loop] SQL injection via string concatenation           │
│                                                              │
│ Languages: Java, C#                                          │
│ CWE-89 (SQL Injection)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Validation Rules

### Input Validation (on write)

- **id**: Matches pattern `[a-z]+(-[a-z]+)*-\d{3}` (e.g., `java-injection-001`)
- **languages**: Non-empty list, each code in Semgrep's official language set
- **message**: Starts with `[The Loop]`, max 200 chars, no newlines
- **severity**: Only `ERROR` or `WARNING`
- **patterns**: Non-empty, valid Semgrep YAML/pattern syntax (validated via `semgrep --validate`)
- **metadata.category**: One of the 6 categories (injection, crypto, security, performance, error-handling, lang-specific)
- **metadata.cwe**: Optional; if provided, format `CWE-\d{1,4}`

### Output Validation (on read)

- **version**: Semantic versioning (major.minor.patch)
- **rules_count**: Integer > 0, matches actual count of rules array
- **rules**: Non-empty array, each item is a valid Rule object
- **created_at**: ISO 8601 timestamp with timezone (always UTC)
- **published_by**: Valid UUID

---

## Error Handling

### 503 Service Unavailable

When `/rules/latest` cannot be retrieved (e.g., no active version, DB error):

```json
{
  "status_code": 503,
  "detail": "No active rule version found"
}
```

Web UI fallback: Display message "No rules published yet. Check back soon."

---

## Backwards Compatibility

The Rule schema is **versioned by `rule_versions.version`**, not by individual rule fields. If rule schema changes in future:

1. Add new field to Rule (e.g., `test_code: string`)
2. Create new RuleVersion with version `v0.5.0` (increment minor version)
3. Old versions (v0.4.0) retain old schema; old clients remain compatible
4. API returns union of both schemas for backwards compatibility

**No breaking changes planned for Phase 1–7 (v0.4.0).**

---

## Migration Path for Spec-018

| Phase | Version | Language | New Rules | Total Rules |
|-------|---------|----------|-----------|-------------|
| Setup | v0.3.0 | Python, JS/TS, Go | 45 | 45 |
| 1 | v0.4.0 | +Java | 15 | 60 |
| 2 | v0.4.0 | +C# | 15 | 75 |
| 3 | v0.4.0 | +PHP | 10 | 85 |
| 4 | v0.4.0 | +Ruby | 10 | 95 |
| 5 | v0.4.0 | +Kotlin | 10 | 105 |
| 6 | v0.4.0 | +Rust | 8 | 113 |
| 7 | v0.4.0 | +C/C++ | 10 | 123 |

**Note**: All phases merge into single RuleVersion (v0.4.0). Migrations update the same row; rules_count increments per phase.
