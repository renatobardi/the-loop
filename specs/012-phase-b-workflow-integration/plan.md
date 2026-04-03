# Phase 5 — Workflow Integration & 14 New Rules (Implementation Plan)

**Status**: Planning → Implementation  
**Spec**: specs/012-phase-b-workflow-integration/spec.md  
**Timeline**: 8-11 dias  
**Branch**: `feat/phase-b-workflow-integration`

---

## Constitution Compliance Check

All 13 mandamentos ✅:

1. **Trunk-based**: Branch `feat/phase-b-workflow-integration` → PR to `main` ✅
2. **Design tokens**: Semgrep rules use shared metadata structure ✅
3. **API explicit**: All endpoints (GET /latest, GET /{version}, POST /publish) documented ✅
4. **Hexagonal**: API maintains domain/ports/adapters layering; workflow is consumer ✅
5. **Single env**: Workflow runs against production API (main = production) ✅
6. **Type hints**: All Python scripts (json_to_semgrep_yaml.py, seed_phase_b.py) use strict typing ✅
7. **SQLAlchemy 2.0**: Existing rule_versions table uses async ORM ✅
8. **Frozen models**: Rule domain models are frozen Pydantic ConfigDict(frozen=True) ✅
9. **Structural changes**: This PR updates CLAUDE.md (workflow patterns) + docs/ (rule usage) ✅
10. **Code as instruction**: Implementation code serves as definitive documentation ✅
11. **Error handling**: Workflow includes fallback to Phase A rules on API timeout/error ✅
12. **Dependencies**: All infra (API, DB, cache, GitHub) pre-exist from Phase B ✅
13. **All dependencies in execution plan**: Tasks include API dependency verification + GitHub token secrets ✅

---

## Architecture Decisions

### Decision 1: Workflow Fetch Strategy

**Choice**: GitHub Actions fetch via `curl` with 5-second timeout + fallback to `.semgrep/theloop-rules.yml.bak`

**Rationale**:
- Stateless: No agent state to manage between runs
- Deterministic: Same rules for same version across all runs
- Observable: Logs clearly show fetch success/failure
- Fail-safe: Fallback ensures workflow never blocks on API unavailability

**Fallback Flow**:
```
workflow start
  ↓
fetch /api/v1/rules/latest (5s timeout)
  ↓
[success] → convert JSON → validate → scan & comment
[timeout/5xx] → use .semgrep/theloop-rules.yml.bak → scan & comment
[invalid JSON] → use fallback → log error
[invalid YAML] → use fallback → log error
```

**Cache Behavior**:
- API cache (300s TTL) means subsequent PRs within 5 min fetch from cache
- Workflow never caches — always calls API (unless API is down → fallback)
- Cache invalidation happens on POST /publish (immediate)

### Decision 2: JSON → YAML Conversion Utility

**Choice**: Standalone Python script `scripts/json_to_semgrep_yaml.py` (not in workflow, run during CI/test phase)

**Rationale**:
- Reusable: Can validate JSON before committing to rules.yml
- Testable: Unit tests for conversion logic
- Transparent: Output visible for code review
- No dependencies: Uses only stdlib (json, yaml, re)

**Conversion Logic**:
```python
def json_to_semgrep_yaml(rules_json: dict) -> str:
    """
    Input: {"rules": [{"id": "...", "patterns": [...], ...}]}
    Output: Valid YAML with 'rules:' top-level key
    Validation:
      - All rule IDs unique
      - All required fields present (id, languages, message, patterns)
      - No duplicate rule IDs with Phase A rules
      - Patterns array non-empty
    """
    # Convert from JSON dict → YAML string
    # Validate via semgrep --validate
    return yaml_string
```

**Execution**: Runs as part of Phase 5 test suite (pytest before workflow PR).

### Decision 3: 14 New Rules Structure

**Principle**: Each rule follows Phase A pattern — multilingual, generic patterns, metadata for future API integration.

**Categories**:

| Category | Rules | Languages | Example Pattern |
|----------|-------|-----------|-----------------|
| **Injection** (3) | path-traversal, xxe, deserialization | generic/python | String concat paths, XXE parsing, pickle/yaml deserialization |
| **Crypto** (2) | weak-md5, weak-random | python/javascript | MD5 hashing, Math.random() instead of crypto.random |
| **Security** (3) | tls-verify-false, jwt-hardcoded, cors-wildcard | generic | `verify=False`, hardcoded secrets in JWT, `Access-Control-Allow-Origin: *` |
| **Performance** (2) | sql-timeout, n-plus-one | python/javascript | SQL without timeout, query in loop |
| **Infrastructure** (1) | docker-root | generic (Dockerfile) | `USER root`, missing `USER non-root` |
| **Config** (2) | hardcoded-url, debug-enabled-prod | generic | Hardcoded API URLs, DEBUG=True in production code |
| **Dependencies** (1) | vulnerable-dependency | generic | Known CVEs in package.json / requirements.txt |

**Rule Metadata** (future-proof for Phase C API):
```yaml
metadata:
  incident_id: "path-traversal-001"
  category: "injection"
  severity: "CRITICAL"
  cwe: "CWE-22"  # Path traversal
  owasp: "A01:2021 – Broken Access Control"
  loop_url: "https://loop.oute.pro/incidents/path-traversal-001"
  remediation: "Use pathlib.Path or os.path.abspath() with validation"
  examples: "malicious_path = '../../../etc/passwd'"
  languages_affected: [python, javascript, java, go, ruby]
```

### Decision 4: Version Pinning Support

**Implementation**: Optional `THELOOP_RULES_VERSION` environment variable in GitHub Actions.

```yaml
env:
  THELOOP_RULES_VERSION: ${{ secrets.THELOOP_RULES_VERSION || '' }}

jobs:
  semgrep-scan:
    steps:
      - name: Fetch Rules
        run: |
          VERSION="${THELOOP_RULES_VERSION:-latest}"
          curl -s "https://api.theloop.oute.pro/api/v1/rules/${VERSION}" \
            --max-time 5 \
            -o rules.json
```

**Use Cases**:
- Default (no env var): Always fetch latest active version
- Pinned (e.g., `0.1.0`): Fetch specific version (even if deprecated, as long as exists)
- Allows rollback without code changes (just update GitHub secret)

### Decision 5: Cache Invalidation Strategy

**Flow on Publish**:
```python
# In POST /api/v1/rules/publish route:
async def publish_version(...):
    # 1. Persist to DB
    version = await service.publish_version(...)
    # 2. Invalidate cache immediately
    await cache.invalidate()
    # 3. Return 201 with version details
    return {"message": "Published", "version": version.version, ...}
```

**Verification Test**:
```bash
# POST v0.2.0
curl -X POST /api/v1/rules/publish -d '{"version": "0.2.0", "rules": [...]}'
# GET /latest before 5s pass → should return v0.2.0 (cache miss)
curl /api/v1/rules/latest
# GET /latest again → should return v0.2.0 (cache hit, <10ms)
curl /api/v1/rules/latest
```

### Decision 6: Rollback Scenario

**Test Flow**:
1. Publish v0.2.0 with intentional bad rule (e.g., ReDoS pattern that always matches)
2. Run workflow → Findings explode, merge blocked
3. Call `POST /api/v1/rules/deprecate` with `version=0.2.0`
   - Sets status='deprecated', deprecated_at=now()
   - Invalidates cache
4. Workflow immediately fetches /latest again
5. Gets v0.1.0 (latest active remaining)
6. Scan passes, merge succeeds

**Success Criteria**: Workflow automatically adopts v0.1.0 without configuration changes.

---

## Technical Implementation

### File Structure (additions to Phase B)

```
.github/workflows/
  theloop-guard.yml              (UPDATED: fetch from API, with fallback)

.semgrep/
  theloop-rules.yml              (UPDATED: v0.2.0 rules + Phase A rules)
  theloop-rules.yml.bak          (NEW: Phase A backup for fallback)

scripts/
  json_to_semgrep_yaml.py        (NEW: JSON → YAML conversion utility)
  seed_phase_b_v0_2_0.py         (NEW: Seed v0.2.0 with 14 new rules)

specs/012-phase-b-workflow-integration/
  spec.md                        (this spec)
  plan.md                        (this file)
  tasks.md                       (detailed task breakdown)
  CLAUDE.md                      (tech guide for workflow patterns)

tests/unit/scripts/
  test_json_to_semgrep_yaml.py   (NEW: conversion logic tests)

tests/integration/
  test_workflow_integration.py    (NEW: E2E workflow tests)
  test_rollback_scenario.py       (NEW: Deprecation + fallback tests)

THELOOP_RULES_v0.2.0.md          (NEW: Docstring for 14 new rules)
```

### Key Files (Phase 5 Focus)

#### 1. `.github/workflows/theloop-guard.yml` (Updated)

```yaml
name: "🔁 The Loop — Incident Guard"
on:
  pull_request:
    branches: [main, master, develop]

jobs:
  semgrep-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      # 1. Checkout
      - uses: actions/checkout@v4
      
      # 2. Fetch rules from API with timeout + fallback
      - name: Fetch rules from API
        id: fetch_rules
        run: |
          VERSION="${{ vars.THELOOP_RULES_VERSION || 'latest' }}"
          curl -s \
            --max-time 5 \
            --connect-timeout 2 \
            -H "Authorization: Bearer ${{ secrets.THELOOP_API_TOKEN }}" \
            "https://theloop-api-1090621437043.us-central1.run.app/api/v1/rules/${VERSION}" \
            -o /tmp/rules.json
          
          if [ $? -ne 0 ]; then
            echo "API timeout or error, using Phase A backup"
            cp .semgrep/theloop-rules.yml.bak /tmp/rules.json
            echo "fallback=true" >> $GITHUB_OUTPUT
          else
            echo "fallback=false" >> $GITHUB_OUTPUT
          fi
      
      # 3. Convert JSON to YAML
      - name: Convert JSON to YAML
        run: |
          python3 scripts/json_to_semgrep_yaml.py \
            --input /tmp/rules.json \
            --output .semgrep/theloop-rules.yml
      
      # 4. Validate YAML
      - name: Validate Semgrep rules
        run: |
          pip install semgrep
          semgrep --validate --config .semgrep/theloop-rules.yml
      
      # 5. Run scan
      - name: Run Semgrep scan
        run: |
          semgrep scan \
            --config .semgrep/theloop-rules.yml \
            --json \
            --output /tmp/semgrep-results.json
      
      # 6. Comment on PR with findings
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            // Parse results, build comment, handle errors/warnings
```

**Key Changes from Phase A**:
- Fetches from API endpoint (v0.2.0 or pinned version)
- Converts JSON to YAML before validation
- Falls back to `.semgrep/theloop-rules.yml.bak` if API unavailable
- Logs fallback status in GITHUB_OUTPUT for observability

#### 2. `scripts/json_to_semgrep_yaml.py` (New)

```python
#!/usr/bin/env python3
"""Convert JSON rules from API to Semgrep YAML format."""

import json
import sys
from pathlib import Path
from typing import Any

def json_to_semgrep_yaml(rules_json: dict[str, Any]) -> str:
    """Convert API JSON rules to Semgrep YAML format."""
    # Validate schema
    if "rules" not in rules_json:
        raise ValueError("Missing 'rules' key in JSON")
    
    rules = rules_json["rules"]
    if not isinstance(rules, list):
        raise ValueError("'rules' must be a list")
    
    # Check for duplicates
    seen_ids = set()
    for rule in rules:
        rule_id = rule.get("id")
        if not rule_id:
            raise ValueError("Rule missing 'id' field")
        if rule_id in seen_ids:
            raise ValueError(f"Duplicate rule ID: {rule_id}")
        seen_ids.add(rule_id)
    
    # Generate YAML header
    yaml_lines = [
        "# theloop-rules.yml",
        "# Generated by The Loop — https://loop.oute.pro",
        f"# Version: {rules_json.get('version', '0.2.0')}",
        "# Updated: " + datetime.now().isoformat(),
        "",
        "rules:",
    ]
    
    # Convert each rule to YAML
    for rule in rules:
        yaml_lines.extend(_rule_to_yaml(rule))
    
    return "\n".join(yaml_lines)

def _rule_to_yaml(rule: dict[str, Any]) -> list[str]:
    """Convert single rule to YAML format."""
    lines = [
        f"  - id: {rule['id']}",
        f"    languages: {rule.get('languages', ['generic'])}",
        f"    message: |",
    ]
    
    # Indent message
    message = rule.get('message', '')
    for line in message.split('\n'):
        lines.append(f"      {line}")
    
    lines.append(f"    severity: {rule.get('severity', 'WARNING')}")
    
    # Add metadata
    if 'metadata' in rule:
        lines.append(f"    metadata:")
        for key, val in rule['metadata'].items():
            if isinstance(val, str):
                lines.append(f"      {key}: \"{val}\"")
            else:
                lines.append(f"      {key}: {val}")
    
    # Add patterns
    if 'patterns' in rule:
        lines.append(f"    patterns:")
        for pattern in rule['patterns']:
            if isinstance(pattern, dict):
                lines.append(f"      - pattern: {pattern.get('pattern', '')}")
            else:
                lines.append(f"      - pattern: {pattern}")
    
    lines.append("")
    return lines

if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output", required=True, help="Output YAML file")
    args = parser.parse_args()
    
    # Load JSON
    with open(args.input) as f:
        data = json.load(f)
    
    # Convert to YAML
    yaml_content = json_to_semgrep_yaml(data)
    
    # Write output
    Path(args.output).write_text(yaml_content)
    print(f"✅ Converted {len(data['rules'])} rules → {args.output}")
```

#### 3. 14 New Rules (Phase 5 Core)

**Structure in `.semgrep/theloop-rules.yml`**:

Each rule follows the Phase A pattern with enhanced metadata:

```yaml
- id: path-traversal-001
  languages: [python, javascript, java, go, ruby, php]
  message: |
    [The Loop] Path traversal vulnerability detected.
    Attacker can access files outside intended directory.
    Incidente: path-traversal-001 | Severidade: CRITICAL
  severity: ERROR
  metadata:
    incident_id: path-traversal-001
    category: injection
    cwe: "CWE-22"
    owasp: "A01:2021 – Broken Access Control"
    loop_url: "https://loop.oute.pro/incidents/path-traversal-001"
    remediation: "Use pathlib.Path.resolve() and verify it's under base directory"
  patterns:
    - pattern-either:
        - pattern: open(user_input, ...)
        - pattern: open($FILE / $USER_INPUT, ...)
        - pattern: $BASE + $USER_PATH
    pattern-not:
        - pattern: open(os.path.abspath(...))
```

**14 Rules Breakdown**:

**Injection (3)**:
- `path-traversal-001` — Path traversal via string concat
- `xxe-001` — XML External Entity injection
- `deserialization-001` — Unsafe deserialization (pickle, yaml)

**Crypto (2)**:
- `crypto-weak-md5-001` — MD5 for hashing (not encryption)
- `crypto-weak-random-001` — Weak random (Math.random vs crypto.random)

**Security (3)**:
- `tls-verify-false-001` — TLS cert verification disabled
- `jwt-hardcoded-001` — Hardcoded JWT secret
- `cors-wildcard-001` — CORS with wildcard origin

**Performance (2)**:
- `sql-timeout-001` — SQL queries without timeout
- `n-plus-one-001` — N+1 query pattern in loops

**Infrastructure (1)**:
- `docker-root-001` — Docker container running as root

**Config (2)**:
- `hardcoded-url-001` — Hardcoded API/service URLs
- `debug-enabled-prod-001` — Debug mode enabled in production

**Dependencies (1)**:
- `dependency-vulnerable-001` — Known vulnerable dependencies (Snyk, npm audit)

### Testing Strategy

#### Unit Tests (10 tests)
`tests/unit/scripts/test_json_to_semgrep_yaml.py`:
- Valid JSON conversion
- Missing 'rules' key → ValueError
- Duplicate rule IDs → ValueError
- Rule missing 'id' field → ValueError
- Metadata serialization (strings, arrays)
- Patterns array conversion
- Escape handling in message text
- Output file creation

#### Integration Tests (6 tests)
`tests/integration/test_workflow_integration.py`:
- API fetch success → rules updated
- API timeout (>5s) → fallback to .bak
- API 500 error → fallback to .bak
- Invalid JSON response → fallback to .bak
- Invalid YAML from conversion → fallback to .bak
- Workflow runs semgrep scan successfully

#### E2E Tests (3 tests)
`tests/integration/test_rollback_scenario.py`:
- Publish v0.2.0 with intentional bad rule
- Deprecate v0.2.0 (status=deprecated, deprecated_at=now)
- Fetch /latest returns v0.1.0 (latest active)
- Workflow scan uses v0.1.0 rules

#### Success Criteria
- ✅ All 19 tests pass (10 unit + 6 integration + 3 E2E)
- ✅ Code coverage ≥ 80% (scripts/ + integration tests)
- ✅ Semgrep validates all 20 rules (6 Phase A + 14 Phase B)
- ✅ Workflow workflow artifact publishes to GitHub Actions
- ✅ Fallback tested (intentional API outage → uses .bak)
- ✅ Version pinning tested (THELOOP_RULES_VERSION env var)

---

## Performance Targets

- **API Fetch**: <5s timeout (hardcoded), hits cache <100ms
- **JSON → YAML Conversion**: <100ms (14 rules = ~2KB JSON → ~5KB YAML)
- **Semgrep Scan**: <30s total (depends on repo size)
- **Workflow Total**: <2min (checkout + fetch + convert + validate + scan + comment)

---

## Rollback Plan

**If v0.2.0 has issues** (e.g., false positive explosion):

1. Call `POST /api/v1/rules/deprecate`:
   ```bash
   curl -X POST \
     -H "Authorization: Bearer $ADMIN_TOKEN" \
     https://api.theloop.oute.pro/api/v1/rules/deprecate \
     -d '{"version": "0.2.0"}'
   ```
2. Cache invalidates immediately
3. Next workflow run fetches /latest → returns v0.1.0 (only active version)
4. All PRs scan with v0.1.0 until v0.2.0 issues fixed

**Time to rollback**: <1 minute (no code changes needed)

---

## Troubleshooting

### Workflow Fetch Timeout

**Symptom**: Workflow log shows "curl timeout"

**Root Cause**: API unreachable or slow (>5s)

**Fix**:
1. Check API health: `curl https://api.theloop.oute.pro/api/v1/health`
2. If unreachable → rollback to v0.1.0 manually
3. If slow → verify PostgreSQL connection in Cloud Run logs

### Invalid YAML Output

**Symptom**: `semgrep --validate` fails

**Root Cause**: json_to_semgrep_yaml.py corrupted rule structure

**Fix**:
1. Inspect /tmp/rules.json → /tmp/semgrep-rules.yml conversion
2. Run locally: `python3 scripts/json_to_semgrep_yaml.py --input /tmp/rules.json --output /tmp/test.yml`
3. Check for missing 'languages' or 'patterns' fields in JSON

### Duplicate Rule IDs

**Symptom**: "Rule ID conflict with existing rules" on publish

**Root Cause**: New rule ID matches Phase A rule (e.g., `injection-001` exists twice)

**Fix**:
1. Rename new rule to avoid collision: `path-traversal-001` not `injection-001`
2. Verify uniqueness before publish: `grep "id:" .semgrep/theloop-rules.yml | sort | uniq -d`

### Fallback Triggered Unexpectedly

**Symptom**: Workflow uses .bak even though API is up

**Root Cause**: 
- Invalid GITHUB_TOKEN (auth failure)
- Malformed JSON response
- Network intermittency

**Fix**:
1. Check GitHub Actions secrets: `THELOOP_API_TOKEN` set?
2. Verify API endpoint returns valid JSON: `curl -H "Authorization: Bearer $TOKEN" /api/v1/rules/latest | jq .`
3. Increase timeout slightly if network flaky: `--max-time 7` instead of `--max-time 5`

---

## Implementation Sequence (6 Phases)

### Phase 1: Workflow Infrastructure (T001–T010)
- Create GitHub Actions workflow template with API fetch + fallback
- Create .semgrep/theloop-rules.yml.bak (Phase A backup)
- Setup GitHub secrets (THELOOP_API_TOKEN)
- Add version pinning support (THELOOP_RULES_VERSION env var)

### Phase 2: JSON Conversion Utility (T011–T020)
- Implement json_to_semgrep_yaml.py with full validation
- Add unit tests (conversion, schema validation, duplicate detection)
- Test with Phase A rules (6 existing rules)
- Verify output passes `semgrep --validate`

### Phase 3: 14 New Rules Definition (T021–T040)
- Define all 14 rules with patterns, metadata, remediation
- Add test patterns (good/ + bad/ code examples)
- Validate each rule individually with semgrep
- Create THELOOP_RULES_v0.2.0.md documentation

### Phase 4: Integration Testing (T041–T050)
- Test API fetch + timeout scenarios
- Test fallback to .bak on various errors
- Test conversion with all 20 rules (6 Phase A + 14 Phase B)
- Test version pinning (THELOOP_RULES_VERSION env var)

### Phase 5: Rollback & Deprecation (T051–T055)
- Add POST /api/v1/rules/deprecate endpoint (if not exists)
- Test deprecation flow (publish v0.2.0 → deprecate → fallback to v0.1.0)
- Document rollback runbook
- Add E2E test for rollback scenario

### Phase 6: Documentation & Merge (T056–T065)
- Update CLAUDE.md with workflow patterns (fetch + fallback, version pinning)
- Update THELOOP.md installation guide for v0.2.0
- Create /docs/rules-catalog.md (all 20 rules reference)
- Code review + merge to main + deploy workflow to GitHub Actions

---

## Files Modified/Created

| Action | File | Purpose |
|--------|------|---------|
| Update | `.github/workflows/theloop-guard.yml` | API fetch + fallback, version pinning |
| Create | `.semgrep/theloop-rules.yml.bak` | Phase A rules backup |
| Create | `scripts/json_to_semgrep_yaml.py` | JSON → YAML conversion utility |
| Create | `scripts/seed_phase_b_v0_2_0.py` | Seed v0.2.0 with 14 new rules |
| Create | `tests/unit/scripts/test_json_to_semgrep_yaml.py` | Conversion unit tests |
| Create | `tests/integration/test_workflow_integration.py` | Fetch + fallback tests |
| Create | `tests/integration/test_rollback_scenario.py` | Deprecation + rollback tests |
| Create | `specs/012-phase-b-workflow-integration/CLAUDE.md` | Tech guide |
| Create | `THELOOP_RULES_v0.2.0.md` | Rule catalog + remediation guide |

---

## Validation Checklist (Pre-Merge)

- [ ] All 19 tests pass (pytest --cov=scripts --cov=tests/integration)
- [ ] Ruff lint: `ruff check scripts/ tests/`
- [ ] Type check: `mypy scripts/`
- [ ] Semgrep validates all 20 rules
- [ ] Workflow file syntax valid: `python3 -m json.tool .github/workflows/theloop-guard.yml`
- [ ] Version pinning tested (env var override)
- [ ] Fallback tested (API down scenario)
- [ ] Rollback scenario tested (deprecate → fetch latest active)
- [ ] CLAUDE.md updated with workflow patterns
- [ ] All documentation complete (THELOOP_RULES_v0.2.0.md, troubleshooting)
- [ ] Code review approved
- [ ] CI gates pass (lint, type-check, test, build)
- [ ] Merge to main + deploy workflow to GitHub Actions

---

**Reference**: specs/011-phase-b-api-integration/ (Phase B API — Base)  
**Next**: specs/013-phase-c-redis-scaling (Phase C — Redis caching)
