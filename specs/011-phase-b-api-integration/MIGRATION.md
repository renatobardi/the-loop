# Phase A → Phase B Migration Guide

**Upgrading from Phase A (static rules) to Phase B (versioned API).**

---

## Overview

**Phase A** (Status: Deprecated):
- Rules hardcoded in `.semgrep/theloop-rules.yml`
- Manual updates (edit file, commit, push)
- No versioning, no rollback capability

**Phase B** (Status: Live):
- Rules fetched dynamically from API
- Automatic updates on new version release
- Version pinning, instant rollback
- Fallback to Phase A rules if API unavailable

**What you need to do**: Enable API fetch in your GitHub Actions workflow.

---

## Step 1: Identify Your Current Setup

**Are you using Phase A?**

```bash
# Phase A setup has this in .github/workflows/
cat .github/workflows/theloop-guard.yml | grep -i "\.semgrep/theloop-rules.yml"

# If you see direct reference to the file, you're on Phase A ✅
```

---

## Step 2: Update GitHub Actions Workflow

Replace the hardcoded rule file with API fetch logic.

### Before (Phase A)

```yaml
# .github/workflows/theloop-guard.yml
steps:
  - name: Checkout
    uses: actions/checkout@v4

  - name: Install Semgrep
    run: pip install semgrep

  - name: Run Semgrep scan
    run: |
      semgrep scan \
        --config .semgrep/theloop-rules.yml \
        --json \
        --output /tmp/semgrep-results.json
```

### After (Phase B)

```yaml
# .github/workflows/theloop-guard.yml
steps:
  - name: Checkout
    uses: actions/checkout@v4

  - name: Fetch rules from API
    id: fetch_rules
    run: |
      VERSION="${{ vars.THELOOP_RULES_VERSION || 'latest' }}"
      curl -s \
        --max-time 5 \
        --connect-timeout 2 \
        "https://theloop-api-1090621437043.us-central1.run.app/api/v1/rules/${VERSION}" \
        -o /tmp/rules.json
      
      if [ $? -ne 0 ]; then
        echo "⚠️  API fetch failed, using Phase A backup"
        cp .semgrep/theloop-rules.yml.bak /tmp/rules.json
        echo "fallback=true" >> $GITHUB_OUTPUT
      else
        echo "fallback=false" >> $GITHUB_OUTPUT
      fi

  - name: Convert JSON to YAML
    run: |
      python3 scripts/json_to_semgrep_yaml.py \
        --input /tmp/rules.json \
        --output .semgrep/theloop-rules.yml

  - name: Install Semgrep
    run: pip install semgrep

  - name: Validate rules YAML
    run: semgrep --validate --config .semgrep/theloop-rules.yml

  - name: Run Semgrep scan
    run: |
      semgrep scan \
        --config .semgrep/theloop-rules.yml \
        --json \
        --output /tmp/semgrep-results.json
```

---

## Step 3: Add Phase A Backup File

Phase B requires a fallback rules file for when API is unavailable.

**If you don't have `.semgrep/theloop-rules.yml.bak`**:

```bash
# Copy current Phase A rules as backup
cp .semgrep/theloop-rules.yml .semgrep/theloop-rules.yml.bak

# Commit
git add .semgrep/theloop-rules.yml.bak
git commit -m "chore: add Phase A rules backup for Phase B fallback"
```

**What's in the backup?**
- All 6 Phase A base rules (static, never updated)
- Used if API fetch fails or times out
- Ensures continuity even if API goes down

---

## Step 4: Add JSON→YAML Conversion Script

Phase B requires converting API JSON response to Semgrep YAML format.

**Create `scripts/json_to_semgrep_yaml.py`**:

```python
#!/usr/bin/env python3
"""Convert API JSON rules to Semgrep YAML format."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

def validate_json(data: dict) -> None:
    """Validate JSON schema matches expected format."""
    if "rules" not in data:
        raise ValueError("Missing 'rules' key in JSON input")
    
    if not isinstance(data["rules"], list):
        raise ValueError("'rules' must be a list")
    
    if len(data["rules"]) == 0:
        raise ValueError("'rules' list cannot be empty")
    
    # Check for duplicates
    seen_ids = set()
    for rule in data["rules"]:
        if "id" not in rule:
            raise ValueError("Rule missing required 'id' field")
        
        rule_id = rule["id"]
        if rule_id in seen_ids:
            raise ValueError(f"Duplicate rule ID: {rule_id}")
        
        seen_ids.add(rule_id)
        
        # Validate required fields
        required_fields = ["id", "languages", "message", "severity", "patterns"]
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Rule '{rule_id}' missing required field: '{field}'")

def rule_to_yaml_lines(rule: dict) -> list[str]:
    """Convert a single rule dict to YAML lines."""
    lines = []
    
    # ID
    lines.append(f"  - id: {rule['id']}")
    
    # Languages
    langs = rule["languages"]
    if isinstance(langs, list):
        langs_str = "[" + ", ".join(langs) + "]"
    else:
        langs_str = str(langs)
    lines.append(f"    languages: {langs_str}")
    
    # Message (support multiline with |)
    message = rule.get("message", "")
    if "\n" in message:
        lines.append("    message: |")
        for msg_line in message.split("\n"):
            lines.append(f"      {msg_line}")
    else:
        lines.append(f"    message: {message}")
    
    # Severity
    lines.append(f"    severity: {rule.get('severity', 'WARNING')}")
    
    # Metadata (if present)
    if "metadata" in rule:
        lines.append("    metadata:")
        for key, val in rule["metadata"].items():
            if isinstance(val, str) and " " in val:
                lines.append(f"      {key}: \"{val}\"")
            else:
                lines.append(f"      {key}: {val}")
    
    # Patterns
    if "patterns" in rule:
        lines.append("    patterns:")
        for pattern in rule["patterns"]:
            if isinstance(pattern, dict):
                # Handle different pattern types
                if "pattern" in pattern:
                    lines.append(f"      - pattern: {pattern['pattern']}")
                elif "pattern-either" in pattern:
                    lines.append("      - pattern-either:")
                    for alt_pattern in pattern["pattern-either"]:
                        lines.append(f"          - pattern: {alt_pattern}")
            else:
                lines.append(f"      - pattern: {pattern}")
    
    return lines

def json_to_semgrep_yaml(rules_json: dict) -> str:
    """Convert API JSON rules to Semgrep YAML format."""
    validate_json(rules_json)
    
    yaml_lines = ["rules:"]
    
    for rule in rules_json["rules"]:
        yaml_lines.extend(rule_to_yaml_lines(rule))
    
    return "\n".join(yaml_lines)

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert API JSON rules to Semgrep YAML format"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file path (from API)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output YAML file path (for Semgrep)",
    )
    
    args = parser.parse_args()
    
    try:
        # Read JSON
        with open(args.input) as f:
            rules_json = json.load(f)
        
        # Convert
        yaml_output = json_to_semgrep_yaml(rules_json)
        
        # Write YAML
        Path(args.output).write_text(yaml_output)
        
        print(f"✅ Converted {len(rules_json['rules'])} rules to {args.output}")
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {args.input}: {e.msg} at line {e.lineno}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Test it**:

```bash
# Make executable
chmod +x scripts/json_to_semgrep_yaml.py

# Test with Phase A rules
python3 scripts/json_to_semgrep_yaml.py \
  --input .semgrep/theloop-rules.yml.bak \
  --output /tmp/test-output.yml

# Verify
semgrep --validate --config /tmp/test-output.yml
```

---

## Step 5: Commit & Push

```bash
# Stage all changes
git add .github/workflows/theloop-guard.yml
git add scripts/json_to_semgrep_yaml.py
git add .semgrep/theloop-rules.yml.bak

# Commit
git commit -m "chore: migrate to Phase B versioned rules API

- Add API fetch step with 5s timeout + fallback to Phase A backup
- Add JSON→YAML conversion for API response
- Add Semgrep validation step before scan
- Update workflow to use version pinning via THELOOP_RULES_VERSION var"

# Push
git push origin your-branch
```

---

## Step 6: Verify Migration

After merge to `main`, check that the workflow runs correctly:

1. **First PR after migration**:
   - Workflow fetches rules from API
   - Conversion succeeds
   - Scan runs with Phase B rules (20 rules total)

2. **Check logs**:
   ```
   ✅ Fetch rules from API: success
   ✅ Convert JSON to YAML: success (20 rules)
   ✅ Validate rules YAML: success
   ✅ Run Semgrep scan: success
   ```

3. **Verify Phase B rules are active**:
   - Look for new rule messages (Phase B rules have "Phase B:" prefix in message)
   - Example: `[The Loop] Path traversal via os.path.join() detected`

---

## Optional: Version Pinning

Want to stay on a specific version (e.g., v0.1.0)?

**In GitHub Settings** (Secrets → New repository variable):
```
Name:  THELOOP_RULES_VERSION
Value: 0.1.0
```

**Workflow uses it**:
```yaml
VERSION="${{ vars.THELOOP_RULES_VERSION || 'latest' }}"
```

Now your repo always uses v0.1.0 rules until you change the variable.

---

## Rollback to Phase A

If something goes wrong and you need to go back:

```bash
# Update workflow to use Phase A rules directly
sed -i 's|Fetch rules from API|Skip API fetch|' .github/workflows/theloop-guard.yml

# Use backup as primary
git checkout .semgrep/theloop-rules.yml.bak > .semgrep/theloop-rules.yml

git commit -m "chore: rollback to Phase A rules"
git push
```

All future PRs will use Phase A rules until you re-enable Phase B.

---

## FAQ

**Q: What happens if the API is down?**  
A: Workflow automatically falls back to Phase A backup rules (.semgrep/theloop-rules.yml.bak). Scanning continues uninterrupted.

**Q: Can I use both Phase A and Phase B rules?**  
A: No — Phase B rules include all Phase A rules, so upgrading gives you everything. Phase A rules are just a fallback.

**Q: How do I disable Phase B and go back to Phase A?**  
A: Remove the API fetch step and conversion logic from workflow, point to static .semgrep/theloop-rules.yml.

**Q: When should I upgrade?**  
A: Whenever new Phase B rules are released that match your tech stack. Conservative orgs can pin a version and update quarterly.

**Q: What if my repo is not in GitHub?**  
A: Phase B API fetch assumes GitHub Actions. For other CI/CD systems (GitLab, Bitbucket, Jenkins), adapt the curl fetch and YAML conversion to your platform.

---

## Support

- **API Status**: https://theloop-api-1090621437043.us-central1.run.app/api/v1/health
- **API Docs**: [API.md](./API.md)
- **Issues**: Report via https://loop.oute.pro/feedback
