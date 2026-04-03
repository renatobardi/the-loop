# The Loop Rules — v0.2.0 Catalog

**Version**: 0.2.0 (20 total rules: 6 Phase A + 14 Phase B)  
**Released**: 2026-04-03  
**API Endpoint**: `GET /api/v1/rules/latest` or `GET /api/v1/rules/0.2.0`  

---

## Overview

v0.2.0 extends The Loop's static analysis capabilities from 6 Phase A rules to 20 rules across 11 categories. All rules are derived from production incidents and are designed for multilingual code scanning.

## What's New in v0.2.0

**Backward Compatible**: All v0.1.0 projects continue scanning with Phase A rules. v0.2.0 adds 14 new rules without breaking changes.

**14 New Rules** across 7 categories:
- **Injection** (3): Path traversal, XXE, unsafe deserialization
- **Crypto** (2): Weak MD5, weak random number generation
- **Security** (3): TLS verify disabled, hardcoded JWT secrets, CORS wildcard
- **Performance** (2): SQL without timeout, N+1 query patterns
- **Infrastructure** (1): Docker running as root
- **Config** (2): Hardcoded URLs, DEBUG enabled in production
- **Dependencies** (1): Known vulnerable dependencies

**How to Upgrade**:
- If using Phase A (v0.1.0): Just update `.semgrep/theloop-rules.yml` to include Phase B rules — no code changes needed
- Existing projects will see 14 additional warnings/errors on next PR
- To stay on Phase A only: Set env var `THELOOP_RULES_VERSION=0.1.0` in GitHub Actions

**Migration Guide**:
| Scenario | Action |
|----------|--------|
| **Stay on Phase A** | Set `THELOOP_RULES_VERSION=0.1.0` in GitHub Actions settings |
| **Migrate to Phase B** | Update `.semgrep/theloop-rules.yml` and review new findings on next PR |
| **Need help?** | Report issues at https://loop.oute.pro/feedback |

---

## Phase A Rules (6 Base Rules)

### Injection Category (2)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `injection-001-sql-string-concat` | ERROR | SQL via string concatenation | Use parametrized queries |
| `injection-002-eval-dynamic-input` | ERROR | `eval()` with dynamic input | Refactor to explicit logic |

### Unsafe API Usage (1)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `unsafe-api-usage-001-shell-injection` | ERROR | `shell=True` with variable | Use `shell=False` + list args |

### Missing Safety Checks (1)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `missing-safety-check-001-hardcoded-secret` | ERROR | Hardcoded credentials | Use env vars or Secret Manager |

### Error Handling (1)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `missing-error-handling-001-bare-except` | WARNING | Bare `except:` clause | Catch specific exceptions |

### Regex (1)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `unsafe-regex-001-redos-pattern` | WARNING | ReDoS pattern `(.+)+` | Avoid nested quantifiers |

---

## Phase B Rules (14 New Rules)

### Injection Category (3)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `path-traversal-001` | ERROR | Path traversal via concat | Use `pathlib.Path.resolve()` |
| `xxe-001` | ERROR | XML External Entity | Use `defusedxml` library |
| `deserialization-001` | ERROR | Unsafe pickle/yaml | Use `json` or `yaml.safe_load()` |

### Crypto Category (2)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `crypto-weak-md5-001` | WARNING | MD5 for hashing | Use SHA256 + salt or bcrypt |
| `crypto-weak-random-001` | WARNING | Weak random (Math.random) | Use `secrets` or `crypto.random` |

### Security Category (3)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `tls-verify-false-001` | ERROR | TLS verify disabled | Remove `verify=False` |
| `jwt-hardcoded-001` | ERROR | Hardcoded JWT secret | Use env var for secret |
| `cors-wildcard-001` | WARNING | CORS with `*` origin | Use explicit domain whitelist |

### Performance Category (2)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `sql-timeout-001` | WARNING | SQL without timeout | Add `timeout` parameter |
| `n-plus-one-001` | WARNING | Query inside loop | Batch query before loop |

### Infrastructure Category (1)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `docker-root-001` | WARNING | Docker runs as root | Add `USER non-root` directive |

### Config Category (2)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `hardcoded-url-001` | WARNING | Hardcoded API URL | Use env var for URL |
| `debug-enabled-prod-001` | WARNING | `DEBUG = True` in code | Use env var for debug flag |

### Dependencies Category (1)

| Rule ID | Severity | Pattern | Remediation |
|---------|----------|---------|-------------|
| `dependency-vulnerable-001` | WARNING | Known vulnerable dependency | Update to patched version |

---

## Usage

### Installation

1. Copy `.semgrep/theloop-rules.yml` to your project
2. Copy `.github/workflows/theloop-guard.yml` to your project
3. Push to trigger workflow on PRs

### Via GitHub Actions

```yaml
# In your .github/workflows/theloop-guard.yml
semgrep scan \
  --config .semgrep/theloop-rules.yml \
  --json \
  --output semgrep-results.json
```

### Via CLI (Local)

```bash
semgrep scan --config .semgrep/theloop-rules.yml
```

### Version Pinning

To use a specific version:

```bash
export THELOOP_RULES_VERSION=0.1.0
curl "https://theloop-api.../api/v1/rules/0.1.0" -o rules.json
```

---

## Severity Levels

- **ERROR**: Blocks PR merge (critical security/reliability issues)
- **WARNING**: Non-blocking (advisory, best practices)

---

## Rollback Procedure

If a rule version causes issues:

1. Call deprecation endpoint:
   ```bash
   curl -X POST https://theloop-api.../api/v1/rules/deprecate \
     -d '{"version": "0.2.0"}'
   ```

2. Workflow automatically fallbacks to latest active version

3. Next PR scan uses previous version

---

## Categories Summary

| Category | Rules | Severity Mix |
|----------|-------|--------------|
| Injection | 5 | 3 ERROR, 2 WARNING |
| Crypto | 2 | 2 WARNING |
| Security | 3 | 2 ERROR, 1 WARNING |
| Performance | 2 | 2 WARNING |
| Infrastructure | 1 | 1 WARNING |
| Config | 2 | 2 WARNING |
| Dependencies | 1 | 1 WARNING |
| Error Handling | 1 | 1 WARNING |
| Unsafe API | 1 | 1 ERROR |
| Regex | 1 | 1 WARNING |
| Missing Safety | 1 | 1 ERROR |

**Total**: 20 rules (8 ERROR, 12 WARNING)

---

## Support

- **Issues**: Report at https://loop.oute.pro/feedback
- **Documentation**: https://loop.oute.pro/docs
- **API**: `https://theloop-api-1090621437043.us-central1.run.app/api/v1`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.2.0 | 2026-04-03 | Added 14 new rules (injection, crypto, security, performance, infra, config, dependencies) |
| 0.1.0 | 2026-03-15 | Initial release with 6 base rules |
