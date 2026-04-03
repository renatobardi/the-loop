# Rule Versioning Strategy

**Document**: Semantic versioning, deprecation, rollback, and lifecycle management for Semgrep rule versions.

---

## Semantic Versioning (X.Y.Z)

All rule versions follow strict semantic versioning format: `MAJOR.MINOR.PATCH`

### Version Components

**MAJOR** (left digit):
- Increment when: **Breaking changes** to existing rules (removal, ID change, incompatible pattern)
- Examples:
  - Removing a rule entirely
  - Changing a rule's ID (e.g., `injection-001` → `sql-injection-001`)
  - Changing pattern behavior significantly (catches different subset)
- **Action**: Requires deprecation of old major version before upgrade

**MINOR** (middle digit):
- Increment when: **New rules added** (non-breaking, additive only)
- Examples:
  - Adding 14 new rules (Phase B)
  - Adding new languages to existing rule (e.g., `python` → `[python, javascript]`)
  - Improving remediation text or metadata
- **Action**: Automatic adoption, no breaking changes

**PATCH** (right digit):
- Increment when: **Bug fixes**, documentation improvements, or pattern refinements
- Examples:
  - Fixing false positives in a rule pattern
  - Correcting remediation text typos
  - Improving regex to catch more edge cases
- **Action**: Automatic adoption, no breaking changes

### Examples

| Version | Type | What Changed | Breaking? |
|---------|------|--------------|-----------|
| 0.1.0 | Initial | 6 Phase A rules | - |
| 0.2.0 | Minor | +14 Phase B rules | No — all additive |
| 0.2.1 | Patch | Fix ReDoS false positive in `unsafe-regex-001` | No |
| 1.0.0 | Major | Remove `missing-error-handling-001` (deprecated) | **Yes** |
| 1.1.0 | Minor | +12 new infrastructure rules | No |

---

## Version Lifecycle

### States

```
DRAFT → ACTIVE → DEPRECATED
  ↓
  (never published)
```

**DRAFT**:
- Version created but not yet published
- Not available to any workflows
- Use case: Testing rule definitions before release
- **Current status**: Not actively used (go straight to ACTIVE on publish)

**ACTIVE**:
- Version published and in use
- `/latest` endpoint returns this version
- All new workflows use this version
- Multiple ACTIVE versions can exist (during transition period)
- **Lifetime**: Until deprecated

**DEPRECATED**:
- Version marked inactive but remains queryable
- Not returned by `/latest` (next ACTIVE version returned instead)
- Still available via `GET /rules/{version}` for rollback
- No new projects adopt this version
- Kept in database for audit trail and rollback capability
- **Lifetime**: Indefinite (never deleted)

### Transition Scenarios

**Scenario 1: Publish v0.2.0 (normal release)**
```
Before:  v0.1.0 (ACTIVE)
         v0.0.1 (DEPRECATED)

Publish v0.2.0

After:   v0.2.0 (ACTIVE)      ← /latest returns this
         v0.1.0 (ACTIVE)      ← still active, can query via /{version}
         v0.0.1 (DEPRECATED)
```

**Scenario 2: Discover issue in v0.2.0, deprecate it (rollback)**
```
Before:  v0.2.0 (ACTIVE)
         v0.1.0 (ACTIVE)

Deprecate v0.2.0

After:   v0.2.0 (DEPRECATED)  ← no longer /latest
         v0.1.0 (ACTIVE)      ← /latest now returns this
```

**Scenario 3: Publish v1.0.0 (remove old rule)**
```
Before:  v0.2.0 (ACTIVE)
         v0.1.0 (ACTIVE)

Publish v1.0.0 (removes `missing-error-handling-001`)

After:   v1.0.0 (ACTIVE)      ← /latest returns this
         v0.2.0 (DEPRECATED)  ← mark deprecated (breaking change)
         v0.1.0 (DEPRECATED)  ← mark deprecated
```

---

## Deprecation Policy

### When to Deprecate

**Automatic deprecation** (required):
1. **Breaking change introduced** (MAJOR version bump)
   - Previous major versions should be deprecated
   - Gives users time to test new version

2. **Critical bug discovered**
   - False positives causing workflow failures
   - Crashes or infinite loops in Semgrep
   - Security issue in rule pattern itself

3. **Replacement rule available**
   - Old rule superseded by improved version
   - Example: `crypto-weak-md5-001` replaced by `crypto-pbkdf2-required-001`

### Manual Deprecation Process

**1. Verify issue**:
```bash
# Check what version is /latest
curl https://api.../api/v1/rules/latest | jq .version

# Check previous version still available
curl https://api.../api/v1/rules/0.1.0 | jq .version
```

**2. Deprecate via API**:
```bash
curl -X POST https://api.../api/v1/rules/deprecate \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"version": "0.2.0"}'

# Response: 200 OK
# {
#   "message": "Deprecated version 0.2.0",
#   "version": "0.2.0",
#   "deprecated_at": "2026-04-05T10:00:00Z"
# }
```

**3. Verify rollback**:
```bash
# /latest should now return v0.1.0
curl https://api.../api/v1/rules/latest | jq .version
# Output: "0.1.0"

# All open PRs will use v0.1.0 on next run
```

**4. Notify users** (phase B onward):
- Post announcement in docs/blog
- Document reason for deprecation
- Link to replacement rule (if applicable)

---

## Rollback Workflow

### Quick Rollback (API Down)

**Scenario**: v0.2.0 published, API crashes during production traffic  
**Goal**: Resume scanning with last known-good version

**Steps**:

1. **Detect**: Monitor alerts show API 500 errors
2. **Deprecate bad version**:
   ```bash
   curl -X POST https://api.../api/v1/rules/deprecate \
     -H "Authorization: Bearer $ADMIN_TOKEN" \
     -d '{"version": "0.2.0"}'
   ```
3. **All running workflows**:
   - Fetch `/latest` → get v0.1.0
   - Use v0.1.0 rules automatically
   - **No workflow code changes needed** ✅

### Pinned Rollback (Version Control)

**Scenario**: Want to keep v0.1.0 rules even after v0.2.0 is released  
**Goal**: Explicitly pin a specific version

**Setup GitHub Actions variable**:
```bash
# In GitHub repo settings:
# Secrets → New repository variable
# Name: THELOOP_RULES_VERSION
# Value: 0.1.0
```

**Workflow uses it**:
```yaml
- name: Fetch rules
  env:
    THELOOP_RULES_VERSION: ${{ vars.THELOOP_RULES_VERSION || 'latest' }}
  run: |
    curl https://api.../api/v1/rules/${THELOOP_RULES_VERSION} -o rules.json
```

**Now**:
- All PRs use v0.1.0 rules
- Change `THELOOP_RULES_VERSION=latest` in GitHub to upgrade
- **Rollback is one-line change** ✅

### Zero-Downtime Rollback

**API still working, but want to revert**:

1. Publish new version (v0.2.1 with fixes):
   ```bash
   curl -X POST https://api.../api/v1/rules/publish \
     -H "Authorization: Bearer $ADMIN_TOKEN" \
     -d @v021_fixes.json
   ```

2. Deprecate bad version:
   ```bash
   curl -X POST https://api.../api/v1/rules/deprecate \
     -d '{"version": "0.2.0"}'
   ```

3. Verify:
   ```bash
   curl https://api.../api/v1/rules/latest | jq .version
   # Output: "0.2.1"
   ```

4. **All in-flight PRs update to v0.2.1** on next workflow run

---

## Compatibility Matrix

### Rule Removal (Breaking Change)

```
v0.1.0: injection-001, injection-002, ... (6 rules)
v0.2.0: injection-001, injection-002, ... + 14 new (20 rules)
v1.0.0: injection-001, ... (remove missing-error-handling-001) (19 rules)
         ↑ BREAKING: clients expecting 6 base rules may break
```

**How to handle**:
- Document removal in CHANGELOG
- Provide migration guide (e.g., "Use crypto-weak-hash-001 instead")
- Deprecate v0.2.0 when v1.0.0 ships
- Keep v0.1.0 and v0.2.0 queryable for rollback

### Language Support Expansion

```
v0.1.0: injection-001 supports [python]
v0.2.0: injection-001 supports [python, javascript] ← ADDITIVE
         ↑ NON-BREAKING: javascript users just get new checks
```

**Impact**: Zero — javascript developers automatically get injection-001 checks when they upgrade to v0.2.0

---

## Version Pinning Examples

### Use Case 1: Conservative Organization

**Policy**: Always stay one version behind stable  
**Setup**:
```bash
# GitHub variable
THELOOP_RULES_VERSION = 0.1.0

# Update quarterly after testing
THELOOP_RULES_VERSION = 0.2.0  # (quarterly review in Jan)
THELOOP_RULES_VERSION = 0.2.1  # (patch, safe to upgrade immediately)
```

### Use Case 2: Aggressive Organization

**Policy**: Always use `/latest`, roll back if issues  
**Setup**:
```bash
# GitHub variable unset (defaults to "latest")

# Auto-upgrade to any new version
# Roll back manually if needed
THELOOP_RULES_VERSION = 0.1.0  # (rollback script)
```

### Use Case 3: Multi-Team Coordination

**Policy**: Staging repo tests new version first, then prod  
**Setup**:
```bash
# Staging repo
THELOOP_RULES_VERSION = latest

# Prod repo (prod uses staging's tested version)
THELOOP_RULES_VERSION = 0.2.0

# After 1 week of staging testing:
THELOOP_RULES_VERSION = latest
```

---

## Maintenance

### Monitoring

**Check version health**:
```bash
# List all versions
curl https://api.../api/v1/rules/versions | jq '.versions[] | {version, status, rules_count}'

# Count active vs deprecated
curl https://api.../api/v1/rules/versions | jq '[.versions[] | .status] | group_by(.) | map({(.[0]): length})'
```

### Cleanup Policy

**Do not delete old versions** — keep indefinitely:
- Rollback requires access to old version
- Audit trail (see version history)
- Minimal storage cost (rules stored as JSON in single row)

**Example**: Year 2030, still queryable:
```bash
curl https://api.../api/v1/rules/0.1.0
# Output: 200 OK with v0.1.0 rules (created 2026-02-01)
```

---

## Decision Tree

**When publishing a new rule version, use this tree**:

```
Is this a breaking change?
├─ YES (removed rule, changed rule ID, incompatible pattern)
│  └─ MAJOR version bump (e.g., 0.1.0 → 1.0.0)
│     └─ Deprecate previous version
│
└─ NO (additive only)
   ├─ Adding new rules or features?
   │  └─ YES → MINOR bump (e.g., 0.1.0 → 0.2.0)
   │
   └─ Fixing bug or improving existing rule?
      └─ PATCH bump (e.g., 0.1.0 → 0.1.1)
```

---

## Reference

- **API Docs**: [API.md](./API.md)
- **Migration Guide**: [MIGRATION.md](./MIGRATION.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
