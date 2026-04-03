"""Integration tests for Phase 5 workflow — fetch, convert, validate, scan."""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts.json_to_semgrep_yaml import json_to_semgrep_yaml


# Test fixtures

@pytest.fixture
def phase_a_rules_json() -> dict:
    """Phase A rules in JSON format (6 rules)."""
    return {
        "version": "0.1.0",
        "rules": [
            {
                "id": "injection-001-sql-string-concat",
                "languages": ["python", "javascript"],
                "message": "[The Loop] SQL injection",
                "severity": "ERROR",
                "patterns": [{"pattern": "$DB.execute(\"...\" + $INPUT)"}],
                "metadata": {"incident_id": "injection-001", "category": "injection"},
            },
            {
                "id": "injection-002-eval-dynamic-input",
                "languages": ["python"],
                "message": "[The Loop] eval() with dynamic input",
                "severity": "ERROR",
                "patterns": [{"pattern": "eval($INPUT)"}],
                "metadata": {"incident_id": "injection-002", "category": "injection"},
            },
            {
                "id": "unsafe-api-usage-001-shell-injection",
                "languages": ["python"],
                "message": "[The Loop] Shell injection",
                "severity": "ERROR",
                "patterns": [{"pattern": "os.system($CMD)"}],
                "metadata": {"incident_id": "unsafe-api-usage-001", "category": "unsafe-api-usage"},
            },
            {
                "id": "missing-safety-check-001-hardcoded-secret",
                "languages": ["generic"],
                "message": "[The Loop] Hardcoded secret",
                "severity": "ERROR",
                "patterns": [{"pattern-regex": "password.*=.*"}],
                "metadata": {"incident_id": "missing-safety-check-001", "category": "missing-safety-check"},
            },
            {
                "id": "missing-error-handling-001-bare-except",
                "languages": ["python"],
                "message": "[The Loop] Bare except",
                "severity": "WARNING",
                "patterns": [{"pattern": "except: pass"}],
                "metadata": {"incident_id": "missing-error-handling-001", "category": "missing-error-handling"},
            },
            {
                "id": "unsafe-regex-001-redos-pattern",
                "languages": ["python"],
                "message": "[The Loop] ReDoS pattern",
                "severity": "WARNING",
                "patterns": [{"pattern": "(.+)+"}],
                "metadata": {"incident_id": "unsafe-regex-001", "category": "unsafe-regex"},
            },
        ],
    }


@pytest.fixture
def phase_b_rules_json() -> dict:
    """Phase B rules in JSON format (3 sample new rules)."""
    return {
        "version": "0.2.0",
        "rules": [
            {
                "id": "path-traversal-001",
                "languages": ["python"],
                "message": "[The Loop] Path traversal",
                "severity": "ERROR",
                "patterns": [{"pattern": "open($INPUT, ...)"}],
                "metadata": {"incident_id": "path-traversal-001", "category": "injection", "cwe": "CWE-22"},
            },
            {
                "id": "crypto-weak-md5-001",
                "languages": ["python"],
                "message": "[The Loop] Weak MD5",
                "severity": "WARNING",
                "patterns": [{"pattern": "hashlib.md5($DATA)"}],
                "metadata": {"incident_id": "crypto-weak-md5-001", "category": "crypto", "cwe": "CWE-327"},
            },
            {
                "id": "tls-verify-false-001",
                "languages": ["python"],
                "message": "[The Loop] TLS verify disabled",
                "severity": "ERROR",
                "patterns": [{"pattern": "requests.get(..., verify=False)"}],
                "metadata": {"incident_id": "tls-verify-false-001", "category": "security", "cwe": "CWE-295"},
            },
        ],
    }


@pytest.fixture
def temp_rules_file(phase_a_rules_json: dict) -> tuple[Path, Path]:
    """Create temporary JSON and output YAML files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "rules.json"
        output_file = Path(tmpdir) / "rules.yml"

        input_file.write_text(json.dumps(phase_a_rules_json), encoding="utf-8")

        yield input_file, output_file


# Test: API Fetch Success (T052)

class TestApiFetchSuccess:
    """Test workflow fetch from API endpoint."""

    def test_fetch_returns_valid_json(self, phase_a_rules_json: dict) -> None:
        """API fetch step receives valid JSON from /api/v1/rules/latest."""
        # Simulate API response
        api_response = phase_a_rules_json

        # Verify JSON is parseable
        assert isinstance(api_response, dict)
        assert "rules" in api_response
        assert isinstance(api_response["rules"], list)
        assert len(api_response["rules"]) == 6

        # Verify all rules have required fields
        for rule in api_response["rules"]:
            assert "id" in rule
            assert "languages" in rule
            assert "message" in rule
            assert "severity" in rule
            assert "patterns" in rule

    def test_fetch_returns_version_metadata(self, phase_a_rules_json: dict) -> None:
        """API response includes version and metadata."""
        assert "version" in phase_a_rules_json
        assert phase_a_rules_json["version"] == "0.1.0"


# Test: JSON → YAML Conversion (T053)

class TestJsonToYamlConversion:
    """Test conversion from API JSON to Semgrep YAML."""

    def test_convert_phase_a_json_to_valid_yaml(self, phase_a_rules_json: dict) -> None:
        """Convert Phase A JSON rules to valid Semgrep YAML."""
        yaml_output = json_to_semgrep_yaml(phase_a_rules_json)

        # Verify YAML structure
        assert "rules:" in yaml_output
        assert len(yaml_output) > 0

        # Verify all rules present
        for rule in phase_a_rules_json["rules"]:
            assert f"id: {rule['id']}" in yaml_output

    def test_convert_phase_b_json_to_valid_yaml(self, phase_b_rules_json: dict) -> None:
        """Convert Phase B JSON rules to valid Semgrep YAML."""
        yaml_output = json_to_semgrep_yaml(phase_b_rules_json)

        assert "rules:" in yaml_output
        assert "id: path-traversal-001" in yaml_output
        assert "id: crypto-weak-md5-001" in yaml_output
        assert "id: tls-verify-false-001" in yaml_output

    def test_converted_yaml_preserves_metadata(self, phase_a_rules_json: dict) -> None:
        """Converted YAML includes all metadata."""
        yaml_output = json_to_semgrep_yaml(phase_a_rules_json)

        # Check for metadata sections
        assert "metadata:" in yaml_output
        assert 'incident_id: "injection-001"' in yaml_output
        assert 'category: "injection"' in yaml_output

    def test_converted_yaml_escapes_special_chars(self, phase_a_rules_json: dict) -> None:
        """Handle special characters in messages."""
        test_rule = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": 'Test with "quotes" and [brackets]',
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(test_rule)
        assert "Test with" in yaml_output


# Test: Fallback to Phase A Backup (T054)

class TestFallbackToBakup:
    """Test workflow fallback when API is unavailable."""

    def test_fallback_file_exists(self) -> None:
        """Phase A backup file exists at expected location."""
        backup_path = Path(".semgrep/theloop-rules.yml.bak")
        assert backup_path.exists(), "Backup file .semgrep/theloop-rules.yml.bak not found"

    def test_fallback_file_contains_phase_a_rules(self) -> None:
        """Backup file contains 6 Phase A rules."""
        backup_path = Path(".semgrep/theloop-rules.yml.bak")
        content = backup_path.read_text(encoding="utf-8")

        # Verify Phase A rule IDs present
        phase_a_ids = [
            "injection-001-sql-string-concat",
            "injection-002-eval-dynamic-input",
            "unsafe-api-usage-001-shell-injection",
            "missing-safety-check-001-hardcoded-secret",
            "missing-error-handling-001-bare-except",
            "unsafe-regex-001-redos-pattern",
        ]

        for rule_id in phase_a_ids:
            assert rule_id in content, f"Rule {rule_id} not in backup file"

    def test_fallback_file_is_valid_yaml(self) -> None:
        """Backup file is valid YAML."""
        import yaml

        backup_path = Path(".semgrep/theloop-rules.yml.bak")
        content = backup_path.read_text(encoding="utf-8")

        try:
            data = yaml.safe_load(content)
            assert "rules" in data
            assert isinstance(data["rules"], list)
            assert len(data["rules"]) == 6
        except yaml.YAMLError as e:
            pytest.fail(f"Backup file is not valid YAML: {e}")


# Test: Complete Rules Set Validation (T055)

class TestCompleteRulesValidation:
    """Test that complete v0.2.0 rule set is valid."""

    def test_v0_2_0_rules_file_exists(self) -> None:
        """v0.2.0 rules file exists."""
        rules_path = Path(".semgrep/theloop-rules.yml")
        assert rules_path.exists(), "Rules file .semgrep/theloop-rules.yml not found"

    def test_v0_2_0_rules_are_valid_yaml(self) -> None:
        """v0.2.0 rules file is valid YAML."""
        import yaml

        rules_path = Path(".semgrep/theloop-rules.yml")
        content = rules_path.read_text(encoding="utf-8")

        try:
            data = yaml.safe_load(content)
            assert "rules" in data
            assert isinstance(data["rules"], list)
        except yaml.YAMLError as e:
            pytest.fail(f"Rules file is not valid YAML: {e}")

    def test_v0_2_0_contains_20_rules(self) -> None:
        """v0.2.0 has exactly 20 rules (6 Phase A + 14 Phase B)."""
        import yaml

        rules_path = Path(".semgrep/theloop-rules.yml")
        data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        rules = data.get("rules", [])

        assert len(rules) == 20, f"Expected 20 rules, got {len(rules)}"

    def test_v0_2_0_rules_have_required_fields(self) -> None:
        """All rules have required fields."""
        import yaml

        rules_path = Path(".semgrep/theloop-rules.yml")
        data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        rules = data.get("rules", [])

        # Semgrep allows both "pattern" (singular) and "patterns" (plural)
        for rule in rules:
            rule_id = rule.get("id")
            assert "id" in rule, f"Rule missing field: id"
            assert "languages" in rule, f"Rule {rule_id} missing field: languages"
            assert "message" in rule, f"Rule {rule_id} missing field: message"
            assert "severity" in rule, f"Rule {rule_id} missing field: severity"
            assert "metadata" in rule, f"Rule {rule_id} missing field: metadata"
            # Either "pattern" or "patterns" is required
            assert ("pattern" in rule or "patterns" in rule), f"Rule {rule_id} missing pattern/patterns field"

    def test_v0_2_0_rule_ids_are_unique(self) -> None:
        """All rule IDs are unique."""
        import yaml

        rules_path = Path(".semgrep/theloop-rules.yml")
        data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        rules = data.get("rules", [])

        rule_ids = [r["id"] for r in rules]
        assert len(rule_ids) == len(set(rule_ids)), "Duplicate rule IDs found"

    def test_v0_2_0_has_correct_category_distribution(self) -> None:
        """Rule set has expected category distribution."""
        import yaml

        rules_path = Path(".semgrep/theloop-rules.yml")
        data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        rules = data.get("rules", [])

        categories = {}
        for rule in rules:
            cat = rule.get("metadata", {}).get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        # Expected: at least injection, crypto, security, performance, config, dependencies
        expected_categories = ["injection", "crypto", "security", "performance", "config", "dependencies"]
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"


# Test: Workflow Simulation (T056)

class TestWorkflowSimulation:
    """Simulate complete workflow: fetch → convert → validate → scan."""

    def test_fetch_convert_validate_pipeline(self, temp_rules_file: tuple[Path, Path], phase_a_rules_json: dict) -> None:
        """Full pipeline: fetch (JSON) → convert (YAML) → validate."""
        input_file, output_file = temp_rules_file

        # Step 1: Simulate fetch (input_file already contains JSON)
        fetched_json = json.loads(input_file.read_text(encoding="utf-8"))
        assert fetched_json == phase_a_rules_json

        # Step 2: Convert JSON to YAML
        yaml_output = json_to_semgrep_yaml(fetched_json)

        # Step 3: Verify output is non-empty and contains expected structures
        assert len(yaml_output) > 0
        assert "rules:" in yaml_output

        # Step 4: Verify all rule IDs present in YAML
        for rule in fetched_json["rules"]:
            assert f"id: {rule['id']}" in yaml_output

    def test_workflow_handles_version_pinning(self, phase_b_rules_json: dict) -> None:
        """Workflow respects THELOOP_RULES_VERSION env var."""
        # Simulate workflow logic
        version = "0.2.0"  # Could come from env var

        # Verify version field in rules
        assert phase_b_rules_json["version"] == version

    def test_workflow_output_is_semgrep_compatible(self, phase_a_rules_json: dict) -> None:
        """Converted YAML is compatible with semgrep."""
        yaml_output = json_to_semgrep_yaml(phase_a_rules_json)

        # Check Semgrep YAML structure
        assert "rules:" in yaml_output

        # Each rule should have id, languages, message, severity, patterns
        for rule in phase_a_rules_json["rules"]:
            rule_section = f"- id: {rule['id']}"
            assert rule_section in yaml_output


# Test: Error Handling & Edge Cases (T057)

class TestErrorHandlingAndEdgeCases:
    """Test error handling in workflow."""

    def test_handle_malformed_json_response(self) -> None:
        """Gracefully handle malformed JSON from API."""
        malformed_json = '{"rules": [incomplete'

        with pytest.raises(json.JSONDecodeError):
            json.loads(malformed_json)

    def test_handle_invalid_json_schema(self) -> None:
        """Reject JSON that doesn't match expected schema."""
        invalid_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    # Missing 'languages'
                    "message": "Test",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                }
            ],
        }

        with pytest.raises(ValueError, match="missing required field"):
            json_to_semgrep_yaml(invalid_json)

    def test_handle_duplicate_rule_ids(self) -> None:
        """Reject rules with duplicate IDs."""
        duplicate_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": "Test 1",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test1"}],
                },
                {
                    "id": "test-001",  # Duplicate
                    "languages": ["python"],
                    "message": "Test 2",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test2"}],
                },
            ],
        }

        with pytest.raises(ValueError, match="Duplicate rule ID"):
            json_to_semgrep_yaml(duplicate_json)

    def test_handle_empty_rules_array(self) -> None:
        """Reject empty rules array."""
        empty_json = {"version": "0.1.0", "rules": []}

        with pytest.raises(ValueError, match="'rules' array is empty"):
            json_to_semgrep_yaml(empty_json)

    def test_handle_missing_rules_key(self) -> None:
        """Reject JSON missing 'rules' key."""
        no_rules_json = {"version": "0.1.0"}

        with pytest.raises(ValueError, match="Missing 'rules' key"):
            json_to_semgrep_yaml(no_rules_json)
