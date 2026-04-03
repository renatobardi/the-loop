# Phase 5 — Workflow Integration & 14 New Rules (Tech Guide)

This document records key technical patterns and decisions for Phase 5 implementation.

---

## Architecture

### Workflow Fetch Logic (GitHub Actions)

```yaml
steps:
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
        echo "Fetch failed, using backup"
        cp .semgrep/theloop-rules.yml.bak /tmp/rules.json
        echo "fallback=true" >> $GITHUB_OUTPUT
      else
        echo "fallback=false" >> $GITHUB_OUTPUT
      fi
```

**Key Points**:
- `--max-time 5`: Hard timeout (5 seconds)
- `--connect-timeout 2`: Connection timeout (2 seconds, nested within max-time)
- Exit code $? = 0 on success, non-zero on timeout/error
- Fallback copies .bak file when curl fails
- Output variable fallback=true/false for later steps

### JSON → YAML Conversion

**Input** (from API `/api/v1/rules/latest`):
```json
{
  "version": "0.2.0",
  "rules": [
    {
      "id": "injection-001",
      "languages": ["python", "javascript"],
      "message": "SQL injection detected",
      "severity": "ERROR",
      "metadata": {
        "incident_id": "injection-001",
        "category": "injection",
        "loop_url": "https://loop.oute.pro/incidents/injection-001"
      },
      "patterns": [
        {
          "pattern": "execute(\"...\" + $VAR)"
        }
      ]
    }
  ]
}
```

**Output** (Semgrep YAML):
```yaml
rules:
  - id: injection-001
    languages: [python, javascript]
    message: |
      SQL injection detected
    severity: ERROR
    metadata:
      incident_id: injection-001
      category: injection
      loop_url: https://loop.oute.pro/incidents/injection-001
    patterns:
      - pattern: execute("..." + $VAR)
```

**Conversion Pseudocode**:
```python
def json_to_semgrep_yaml(rules_json: dict) -> str:
    # 1. Validate schema
    assert "rules" in rules_json, "Missing 'rules' key"
    assert isinstance(rules_json["rules"], list), "'rules' must be list"
    
    # 2. Check for duplicates
    seen_ids = set()
    for rule in rules_json["rules"]:
        if rule["id"] in seen_ids:
            raise ValueError(f"Duplicate rule ID: {rule['id']}")
        seen_ids.add(rule["id"])
    
    # 3. Generate YAML
    yaml_lines = ["rules:"]
    for rule in rules_json["rules"]:
        yaml_lines.extend(_rule_to_yaml(rule))
    
    return "\n".join(yaml_lines)

def _rule_to_yaml(rule: dict) -> list[str]:
    lines = [
        f"  - id: {rule['id']}",
        f"    languages: {rule['languages']}",
        f"    message: |"
    ]
    # Indent message
    for line in rule['message'].split('\n'):
        lines.append(f"      {line}")
    
    lines.append(f"    severity: {rule['severity']}")
    
    # Metadata
    if 'metadata' in rule:
        lines.append("    metadata:")
        for key, val in rule['metadata'].items():
            lines.append(f"      {key}: {val}")
    
    # Patterns
    if 'patterns' in rule:
        lines.append("    patterns:")
        for pattern in rule['patterns']:
            lines.append(f"      - pattern: {pattern['pattern']}")
    
    return lines
```

### Fallback Strategy

**Trigger Conditions**:
1. curl exit code != 0 (timeout, connection refused, DNS failure)
2. HTTP 5xx response (API error)
3. Invalid JSON response (malformed)
4. JSON → YAML conversion fails (schema violation)

**Fallback File**: `.semgrep/theloop-rules.yml.bak`
- Contains Phase A rules (6 rules) in YAML format
- Created once during Phase 1 setup
- Never updated after (backup is static for safety)
- Path hardcoded in workflow (no variable substitution)

**Recovery Path**:
```
workflow detects error
  ↓
copies .bak to .semgrep/theloop-rules.yml
  ↓
runs semgrep with fallback rules
  ↓
logs "Using Phase A backup (v0.1.0)" in workflow output
  ↓
PR scan proceeds with v0.1.0
```

### Version Pinning

**Mechanism**: Environment variable `THELOOP_RULES_VERSION` (GitHub Actions secret or variable)

```yaml
env:
  THELOOP_RULES_VERSION: ${{ secrets.THELOOP_RULES_VERSION || '' }}

steps:
  - run: |
      VERSION="${THELOOP_RULES_VERSION:-latest}"
      curl ... "/.../api/v1/rules/${VERSION}"
```

**Usage**:
- **Unset or empty string**: Fetches `/api/v1/rules/latest` (current behavior)
- **Set to semver** (e.g., `0.1.0`): Fetches `/api/v1/rules/0.1.0` (specific version)
- **Use case**: Rollback without changing workflow code

**Example Rollback Flow**:
1. v0.2.0 published, has issue
2. Set `THELOOP_RULES_VERSION=0.1.0` in GitHub secret
3. Next PR run fetches v0.1.0 automatically
4. All PRs use v0.1.0 until issue fixed

### Cache Invalidation on Publish

**In API** (Phase B carry-forward):
```python
async def publish_version(...):
    # Save to DB
    version = await service.publish_version(...)
    
    # Invalidate cache (immediate)
    await cache.invalidate()
    
    # Return 201
    return {"message": "Published", "version": version.version}
```

**In Workflow** (Phase 5):
- Workflow never caches (always calls API or uses fallback)
- Cache lives in API process (not in workflow runner)
- Subsequent workflow runs within 5 minutes hit API cache
- Published v0.2.0 visible to all subsequent runs immediately

---

## 14 New Rules (Pattern Reference)

### Injection (3)

**path-traversal-001**:
```python
# Bad
user_path = request.args['path']
open(base_dir + user_path)  # ← Vulnerable to ../../../etc/passwd

# Good
user_path = request.args['path']
safe_path = (Path(base_dir) / user_path).resolve()
assert str(safe_path).startswith(str(base_dir))
open(safe_path)
```

**xxe-001**:
```python
# Bad
import xml.etree.ElementTree as ET
tree = ET.parse(user_xml_url)  # ← XXE: parser fetches external entities

# Good
from defusedxml.ElementTree import parse
tree = parse(user_xml_url)
```

**deserialization-001**:
```python
# Bad
import pickle
obj = pickle.loads(user_data)  # ← Arbitrary code execution

# Good
import json
obj = json.loads(user_data)
```

### Crypto (2)

**crypto-weak-md5-001**:
```python
# Bad
import hashlib
hash = hashlib.md5(password).hexdigest()  # ← Not collision-resistant

# Good
import hashlib, os
salt = os.urandom(32)
hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
```

**crypto-weak-random-001**:
```python
# Bad (Python)
import random
token = random.randint(0, 2**32)

# Bad (JavaScript)
token = Math.random().toString(36)

# Good (Python)
import secrets
token = secrets.token_hex(32)

# Good (JavaScript)
const token = crypto.getRandomValues(new Uint8Array(32))
```

### Security (3)

**tls-verify-false-001**:
```python
# Bad
import requests
requests.get('https://...', verify=False)  # ← Man-in-the-middle possible

# Good
import requests
requests.get('https://...', verify='/path/to/ca.crt')
# OR use system CA bundle (default)
requests.get('https://...')
```

**jwt-hardcoded-001**:
```python
# Bad
SECRET_KEY = "my-super-secret-key-12345"
token = jwt.encode({'user_id': 123}, SECRET_KEY)

# Good
import os
SECRET_KEY = os.environ['JWT_SECRET']
token = jwt.encode({'user_id': 123}, SECRET_KEY)
```

**cors-wildcard-001**:
```python
# Bad (Flask)
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# Good
from flask_cors import CORS
CORS(app, origins=['https://example.com', 'https://app.example.com'])
```

### Performance (2)

**sql-timeout-001**:
```python
# Bad
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Good
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,), timeout=30)
```

**n-plus-one-001**:
```python
# Bad
users = User.query.all()
for user in users:
    print(user.profile.bio)  # ← Query per user (N+1)

# Good
users = User.query.options(joinedload(User.profile)).all()
for user in users:
    print(user.profile.bio)  # ← Single query with join
```

### Infrastructure (1)

**docker-root-001**:
```dockerfile
# Bad
FROM python:3.12
COPY . /app
WORKDIR /app
# No USER directive ← runs as root

# Good
FROM python:3.12
COPY . /app
WORKDIR /app
RUN useradd -m appuser
USER appuser
```

### Config (2)

**hardcoded-url-001**:
```python
# Bad
API_URL = "https://api.production.example.com/v1"
DATABASE_URL = "postgresql://user:pass@prod-db.example.com:5432/db"

# Good
import os
API_URL = os.environ['API_URL']
DATABASE_URL = os.environ['DATABASE_URL']
```

**debug-enabled-prod-001**:
```python
# Bad
DEBUG = True  # ← In production code
app = Flask(__name__)
app.run(debug=DEBUG)

# Good
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
```

### Dependencies (1)

**dependency-vulnerable-001**:
- Pattern: Scan `package.json` + `requirements.txt` for known CVEs
- Tools: npm audit, pip-audit, Snyk
- Example: Dependency with `npm audit | grep CRITICAL`

---

## Testing Patterns

### Unit Test Example (json_to_semgrep_yaml.py)

```python
import pytest
from scripts.json_to_semgrep_yaml import json_to_semgrep_yaml

def test_valid_json_conversion():
    """Convert valid Phase A rules to YAML."""
    input_json = {
        "version": "0.1.0",
        "rules": [
            {
                "id": "injection-001",
                "languages": ["python"],
                "message": "SQL injection",
                "severity": "ERROR",
                "patterns": [
                    {"pattern": "execute(\"...\" + $VAR)"}
                ]
            }
        ]
    }
    
    yaml_output = json_to_semgrep_yaml(input_json)
    
    assert "rules:" in yaml_output
    assert "id: injection-001" in yaml_output
    assert "languages: ['python']" in yaml_output or "languages: [python]" in yaml_output

def test_missing_rules_key():
    """Reject JSON without 'rules' key."""
    input_json = {"version": "0.1.0"}  # Missing 'rules'
    
    with pytest.raises(ValueError, match="Missing 'rules' key"):
        json_to_semgrep_yaml(input_json)

def test_duplicate_rule_ids():
    """Detect and reject duplicate rule IDs."""
    input_json = {
        "version": "0.2.0",
        "rules": [
            {"id": "injection-001", "patterns": [...]},
            {"id": "injection-001", "patterns": [...]}  # Duplicate
        ]
    }
    
    with pytest.raises(ValueError, match="Duplicate rule ID"):
        json_to_semgrep_yaml(input_json)
```

### Integration Test Example (Workflow Fetch)

```python
import asyncio
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_api_fetch_success(tmp_path):
    """Workflow fetches from API successfully."""
    rules_json = {"version": "0.2.0", "rules": [...]}
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = rules_json
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Simulate workflow fetch
        rules = await fetch_rules_from_api("https://api.../latest", timeout=5)
        
        assert rules == rules_json
        assert len(rules["rules"]) == 20  # 6 Phase A + 14 Phase B

@pytest.mark.asyncio
async def test_api_timeout_uses_fallback(tmp_path):
    """Workflow falls back to .bak when API times out."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.side_effect = asyncio.TimeoutError()
        
        # Simulate workflow with fallback
        rules = await fetch_rules_from_api("https://api.../latest", timeout=5)
        rules = load_fallback_rules(".semgrep/theloop-rules.yml.bak")
        
        assert len(rules["rules"]) == 6  # Phase A fallback
```

### E2E Test Example (Rollback Scenario)

```python
@pytest.mark.asyncio
async def test_rollback_deprecate_version():
    """Publish v0.2.0 → deprecate → fetch /latest returns v0.1.0."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Publish v0.2.0
        response = await client.post(
            "/api/v1/rules/publish",
            json={
                "version": "0.2.0",
                "rules": [...],
                "notes": "Phase B with 14 new rules"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # 2. Verify /latest returns v0.2.0
        response = await client.get("/api/v1/rules/latest")
        assert response.json()["version"] == "0.2.0"
        
        # 3. Deprecate v0.2.0
        response = await client.post(
            "/api/v1/rules/deprecate",
            json={"version": "0.2.0"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # 4. Verify /latest returns v0.1.0 (next active)
        response = await client.get("/api/v1/rules/latest")
        assert response.json()["version"] == "0.1.0"
```

---

## Common Patterns

### Workflow Fetch with Retry

```yaml
- name: Fetch rules with retry
  run: |
    MAX_RETRIES=3
    RETRY=0
    
    while [ $RETRY -lt $MAX_RETRIES ]; do
      curl -s --max-time 5 \
        "https://api.../api/v1/rules/latest" \
        -o /tmp/rules.json && break
      RETRY=$((RETRY + 1))
      sleep 1
    done
    
    if [ ! -f /tmp/rules.json ]; then
      cp .semgrep/theloop-rules.yml.bak /tmp/rules.json
      echo "⚠️ Using fallback after 3 retries"
    fi
```

### Workflow Logging

```yaml
- name: Log fetch result
  run: |
    echo "📋 Rules Fetch Summary:"
    echo "  Version: $(cat /tmp/rules.json | jq -r '.version')"
    echo "  Rules Count: $(cat /tmp/rules.json | jq '.rules | length')"
    echo "  Fallback Used: ${{ steps.fetch_rules.outputs.fallback }}"
```

### Error Handling in Python

```python
import json
from pathlib import Path

def load_json_safely(filepath: str) -> dict:
    """Load JSON with detailed error reporting."""
    try:
        with open(filepath) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Rules file not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {filepath}: {e.msg} at line {e.lineno}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error loading {filepath}: {type(e).__name__}: {e}")
```

---

## Troubleshooting

### API Fetch Timeout

**Symptom**: Workflow log shows `curl: (28) Operation timeout. The timeout specified has expired.`

**Root Cause**: API endpoint unreachable or slow (>5s)

**Fix**:
1. Check API health: `curl https://theloop-api-1090621437043.us-central1.run.app/api/v1/health`
2. Check logs: `gcloud run logs read theloop-api --region=us-central1 --limit=50`
3. If API is down, fallback will automatically use .bak

### JSON → YAML Conversion Fails

**Symptom**: Workflow log shows `ValueError: Invalid JSON in /tmp/rules.json`

**Root Cause**: API response is malformed or not valid JSON

**Fix**:
1. Inspect API response: `curl https://api.../api/v1/rules/latest | jq .`
2. Check for non-JSON response (e.g., HTML error page)
3. Fallback will use .bak if conversion fails

### Duplicate Rule IDs on Publish

**Symptom**: `POST /api/v1/rules/publish` returns 400 with "Duplicate rule ID"

**Root Cause**: New rule ID conflicts with existing rule (e.g., `injection-001` exists in Phase A)

**Fix**:
1. Verify Phase B rule IDs are unique: `grep "id:" .semgrep/theloop-rules.yml | sort | uniq -d`
2. Rename conflicting rule: Use prefixes like `path-traversal-001`, `xxe-001`, etc.
3. Re-publish with unique IDs

### Fallback Triggered Unexpectedly

**Symptom**: Workflow uses `.bak` even though API is up

**Root Cause**:
- THELOOP_API_TOKEN not set or incorrect
- Network connectivity issue
- Malformed Authorization header

**Fix**:
1. Verify GitHub secret: `gh secret list | grep THELOOP_API_TOKEN`
2. Test curl manually: `curl -H "Authorization: Bearer $TOKEN" https://api.../api/v1/rules/latest`
3. Check Network tab in GitHub Actions logs for actual HTTP response
4. Consider increasing `--connect-timeout 2` to `--connect-timeout 5` if flaky network

### Semgrep Validation Fails

**Symptom**: Workflow step "Validate Semgrep rules" fails

**Root Cause**: YAML syntax error or missing required field

**Fix**:
1. Run locally: `semgrep --validate --config .semgrep/theloop-rules.yml`
2. Check for YAML indentation (4-space is standard)
3. Verify all rules have required fields: id, languages, message, severity, patterns
4. Look at Semgrep error message for exact line number

---

## Performance Considerations

### API Cache Hit Rate

**Goal**: >80% of workflow runs hit cached version (<100ms response)

**Calculation**:
- v0.2.0 published at time T=0
- Cache TTL = 300s (5 minutes)
- 20 PRs created between T=0 and T=300
- Expected cache hits: 19/20 = 95% ✅

**Optimization**: If cache hit rate is low, increase TTL in Phase B API cache (currently 300s).

### Workflow Total Duration

**Breakdown**:
```
checkout:                5s
install semgrep:         3s
fetch rules:            <1s (cached) or <100ms (fallback)
convert JSON→YAML:      <100ms
validate YAML:          <500ms
scan repo:             10-30s (depends on repo size)
comment PR:            <1s
───────────────────────────
TOTAL:                  20-45s
```

**Optimization**: Parallel steps where possible (fetch + install can overlap).

---

## Code Style

- **Type hints**: All functions must have return types
- **Async**: Use `async def` + `await` for I/O operations
- **Error handling**: Specific exception types (json.JSONDecodeError, ValueError, TimeoutError)
- **Import organization**: Sort alphabetically, no `__future__` imports
- **Semgrep patterns**: Use `pattern-either` for multiple patterns, `pattern-not` for exclusions

---

**Reference**: specs/011-phase-b-api-integration/CLAUDE.md (Phase B patterns)  
**Next**: specs/013-phase-c-redis-scaling (Phase C — Redis caching)
