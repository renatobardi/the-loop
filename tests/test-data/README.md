# The Loop Test Data — Vulnerability & Fix Samples

This directory contains intentionally vulnerable code (`bad/`) and corrected code (`good/`) for validating The Loop incident guard.

## Structure

```
bad/                  ← Intentionally vulnerable patterns
├── injection.py      ← SQL injection + eval() patterns
├── shell.py          ← Shell injection patterns
├── secrets.py        ← Hardcoded credentials
└── error_handling.py ← Bare except blocks

good/                 ← Corrected, safe patterns
├── injection_safe.py
├── shell_safe.py
├── secrets_safe.py
└── error_handling_safe.py
```

## Expected Rule Matches

### From `bad/` directory (should match):

| File | Rules That Should Fire | Count | Severity |
|------|---|---|---|
| `injection.py` | injection-001, injection-002 | 2 | ERROR |
| `shell.py` | unsafe-api-usage-001 | 4 | ERROR |
| `secrets.py` | missing-safety-check-001 | 5 | ERROR |
| `error_handling.py` | missing-error-handling-001 | 4 | WARNING |
| **TOTAL** | — | **15 findings** | 13 ERROR, 2 WARNING |

### From `good/` directory (should match):

| File | Rules That Should Fire | Count |
|------|---|---|
| `injection_safe.py` | (none) | 0 |
| `shell_safe.py` | (none) | 0 |
| `secrets_safe.py` | (none) | 0 |
| `error_handling_safe.py` | (none) | 0 |
| **TOTAL** | — | **0 findings** |

## Validation Tests

### Test 1: Scan bad/ — Should detect all patterns

```bash
semgrep scan bad/ --config .semgrep/theloop-rules.yml --json
```

**Expected**: 15 findings total (13 ERROR, 2 WARNING)

### Test 2: Scan good/ — Should detect nothing

```bash
semgrep scan good/ --config .semgrep/theloop-rules.yml --json
```

**Expected**: 0 findings (100% safe)

### Test 3: GitHub Actions workflow on test repo

Push both `bad/` and `good/` code in separate PRs and verify:

1. **PR with bad/ code**: Workflow reports findings, ERROR findings block merge
2. **PR with good/ code**: Workflow reports "✅ Clean", merge allowed

## Usage in the-loop-tester

This test data is copied to the public test repository: [renatobardi/the-loop-tester](https://github.com/renatobardi/the-loop-tester)

### For developers:
- Learn what patterns to avoid by reading `bad/` code
- Learn correct approaches by reading `good/` code

### For validation:
- Open PRs that add files from `bad/` directory
- Verify rules fire correctly
- Open PRs with `good/` code
- Verify no false positives

## Notes

- All files are Python (Python is most universal language; rules also support JS, Go, Java, Ruby)
- `bad/` files are intentionally **non-functional** (missing imports, undefined variables) — they're designed for pattern matching, not execution
- `good/` files are **functional** — they show real-world correct patterns

## Adding More Tests

To add a new vulnerable pattern:

1. Create file in `bad/` with the vulnerable pattern
2. Create corresponding safe version in `good/`
3. Verify the rule fires/doesn't fire as expected
4. Document in the table above
