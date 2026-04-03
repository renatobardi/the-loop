"""Unit tests for scripts/json_to_semgrep_yaml.py — JSON to YAML conversion utility."""

import json
import tempfile
from pathlib import Path

import pytest

from scripts.json_to_semgrep_yaml import _rule_to_yaml, json_to_semgrep_yaml


class TestJsonToSemgrepYaml:
    """Tests for json_to_semgrep_yaml() conversion function."""

    def test_valid_phase_a_conversion(self) -> None:
        """Convert valid Phase A rules (6 rules) to YAML."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "injection-001",
                    "languages": ["python", "javascript"],
                    "message": "SQL injection via string concat",
                    "severity": "ERROR",
                    "patterns": [
                        {"pattern": "execute(\"...\" + $VAR)"}
                    ],
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        assert "rules:" in yaml_output
        assert "id: injection-001" in yaml_output
        assert "languages:" in yaml_output
        assert "message:" in yaml_output
        assert "severity: ERROR" in yaml_output
        assert "patterns:" in yaml_output

    def test_missing_rules_key(self) -> None:
        """Reject JSON without 'rules' key."""
        input_json = {"version": "0.1.0"}

        with pytest.raises(ValueError, match="Missing 'rules' key"):
            json_to_semgrep_yaml(input_json)

    def test_rules_not_list(self) -> None:
        """Reject 'rules' that is not a list."""
        input_json = {"version": "0.1.0", "rules": "not-a-list"}

        with pytest.raises(ValueError, match="'rules' must be a list"):
            json_to_semgrep_yaml(input_json)

    def test_empty_rules_array(self) -> None:
        """Reject empty 'rules' array."""
        input_json = {"version": "0.1.0", "rules": []}

        with pytest.raises(ValueError, match="'rules' array is empty"):
            json_to_semgrep_yaml(input_json)

    def test_missing_rule_id(self) -> None:
        """Reject rule without 'id' field."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "languages": ["python"],
                    "message": "Test",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                }
            ],
        }

        with pytest.raises(ValueError, match="missing required 'id' field"):
            json_to_semgrep_yaml(input_json)

    def test_duplicate_rule_ids(self) -> None:
        """Detect and reject duplicate rule IDs."""
        input_json = {
            "version": "0.2.0",
            "rules": [
                {
                    "id": "injection-001",
                    "languages": ["python"],
                    "message": "Test 1",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test1"}],
                },
                {
                    "id": "injection-001",  # Duplicate!
                    "languages": ["javascript"],
                    "message": "Test 2",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test2"}],
                },
            ],
        }

        with pytest.raises(ValueError, match="Duplicate rule ID detected: 'injection-001'"):
            json_to_semgrep_yaml(input_json)

    def test_missing_required_field_languages(self) -> None:
        """Reject rule missing 'languages' field."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "message": "Test",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                    # Missing 'languages'
                }
            ],
        }

        with pytest.raises(ValueError, match="missing required field: 'languages'"):
            json_to_semgrep_yaml(input_json)

    def test_missing_required_field_message(self) -> None:
        """Reject rule missing 'message' field."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                    # Missing 'message'
                }
            ],
        }

        with pytest.raises(ValueError, match="missing required field: 'message'"):
            json_to_semgrep_yaml(input_json)

    def test_missing_required_field_severity(self) -> None:
        """Reject rule missing 'severity' field."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": "Test",
                    "patterns": [{"pattern": "test"}],
                    # Missing 'severity'
                }
            ],
        }

        with pytest.raises(ValueError, match="missing required field: 'severity'"):
            json_to_semgrep_yaml(input_json)

    def test_missing_required_field_patterns(self) -> None:
        """Reject rule missing 'patterns' field."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": "Test",
                    "severity": "ERROR",
                    # Missing 'patterns'
                }
            ],
        }

        with pytest.raises(ValueError, match="missing required field: 'patterns'"):
            json_to_semgrep_yaml(input_json)

    def test_metadata_serialization(self) -> None:
        """Serialize metadata correctly (strings, lists, numbers)."""
        input_json = {
            "version": "0.2.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": "Test with metadata",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                    "metadata": {
                        "incident_id": "test-001",
                        "category": "injection",
                        "cwe": "CWE-123",
                        "languages_affected": ["python", "javascript"],
                        "priority": 1,
                    },
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        assert 'incident_id: "test-001"' in yaml_output
        assert 'category: "injection"' in yaml_output
        assert 'cwe: "CWE-123"' in yaml_output
        assert "languages_affected: [python, javascript]" in yaml_output
        assert "priority: 1" in yaml_output

    def test_multiline_message(self) -> None:
        """Handle multiline messages correctly."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": "Line 1\nLine 2\nLine 3",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        lines = yaml_output.split("\n")
        # Find message section and verify indentation
        message_idx = next(i for i, line in enumerate(lines) if "message: |" in line)
        assert lines[message_idx + 1].startswith("      Line 1")
        assert lines[message_idx + 2].startswith("      Line 2")
        assert lines[message_idx + 3].startswith("      Line 3")

    def test_pattern_either(self) -> None:
        """Handle pattern-either correctly."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": "Test",
                    "severity": "ERROR",
                    "patterns": [
                        {
                            "pattern-either": [
                                "pattern1()",
                                "pattern2()",
                                "pattern3()",
                            ]
                        }
                    ],
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        assert "pattern-either:" in yaml_output
        assert "pattern1()" in yaml_output
        assert "pattern2()" in yaml_output
        assert "pattern3()" in yaml_output

    def test_pattern_not(self) -> None:
        """Handle pattern-not correctly."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": "Test",
                    "severity": "ERROR",
                    "patterns": [
                        {"pattern": "main_pattern()"},
                        {
                            "pattern-not": [
                                "exception_pattern1()",
                                "exception_pattern2()",
                            ]
                        },
                    ],
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        assert "pattern: main_pattern()" in yaml_output
        assert "pattern-not:" in yaml_output
        assert "exception_pattern1()" in yaml_output
        assert "exception_pattern2()" in yaml_output

    def test_pattern_regex(self) -> None:
        """Handle pattern-regex correctly."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["generic"],
                    "message": "Test",
                    "severity": "ERROR",
                    "patterns": [
                        {
                            "pattern-regex": r"(?i)(password|secret)\s*=\s*[\"'][A-Za-z0-9]+[\"']"
                        }
                    ],
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        assert "pattern-regex:" in yaml_output

    def test_path_exclusions(self) -> None:
        """Handle path exclusions in rules."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["generic"],
                    "message": "Test",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                    "paths": {
                        "exclude": [
                            "*.test.*",
                            "*.spec.*",
                            "tests/",
                            ".env.example",
                        ]
                    },
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        assert "paths:" in yaml_output
        assert "exclude:" in yaml_output
        assert "*.test.*" in yaml_output
        assert "tests/" in yaml_output

    def test_escaped_quotes_in_strings(self) -> None:
        """Escape internal quotes in metadata strings."""
        input_json = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": 'Test with "quotes" inside',
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                    "metadata": {
                        "remediation": 'Use "safe" method instead',
                    },
                }
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        assert 'remediation: "Use \\"safe\\" method instead"' in yaml_output

    def test_multiple_rules(self) -> None:
        """Convert multiple rules (3 rules)."""
        input_json = {
            "version": "0.2.0",
            "rules": [
                {
                    "id": "injection-001",
                    "languages": ["python"],
                    "message": "SQL injection",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "execute(\"...\" + $VAR)"}],
                },
                {
                    "id": "crypto-001",
                    "languages": ["python", "javascript"],
                    "message": "Weak random",
                    "severity": "WARNING",
                    "patterns": [{"pattern": "Math.random()"}],
                },
                {
                    "id": "security-001",
                    "languages": ["generic"],
                    "message": "Hardcoded secret",
                    "severity": "ERROR",
                    "patterns": [{"pattern-regex": r"(password|secret)\s*="}],
                },
            ],
        }

        yaml_output = json_to_semgrep_yaml(input_json)

        # Verify all 3 rules present
        assert "id: injection-001" in yaml_output
        assert "id: crypto-001" in yaml_output
        assert "id: security-001" in yaml_output

        # Verify rule count
        rule_count = yaml_output.count("- id:")
        assert rule_count == 3


class TestRuleToYaml:
    """Tests for _rule_to_yaml() helper function."""

    def test_simple_rule(self) -> None:
        """Convert simple rule to YAML lines."""
        rule = {
            "id": "test-001",
            "languages": ["python"],
            "message": "Test message",
            "severity": "ERROR",
            "patterns": [{"pattern": "test_pattern"}],
        }

        lines = _rule_to_yaml(rule)

        yaml_text = "\n".join(lines)
        assert "id: test-001" in yaml_text
        assert "languages: [python]" in yaml_text
        assert "message: |" in yaml_text
        assert "Test message" in yaml_text
        assert "severity: ERROR" in yaml_text
        assert "pattern: test_pattern" in yaml_text

    def test_rule_with_multiple_languages(self) -> None:
        """Format multiple languages in array."""
        rule = {
            "id": "test-001",
            "languages": ["python", "javascript", "java"],
            "message": "Test",
            "severity": "WARNING",
            "patterns": [{"pattern": "test"}],
        }

        lines = _rule_to_yaml(rule)
        yaml_text = "\n".join(lines)

        assert "languages: [python, javascript, java]" in yaml_text

    def test_rule_defaults(self) -> None:
        """Use sensible defaults when fields not provided."""
        rule = {
            "id": "test-001",
            "languages": ["python"],
            "message": "Test",
            # No severity provided
            # No metadata provided
            "patterns": [{"pattern": "test"}],
        }

        lines = _rule_to_yaml(rule)
        yaml_text = "\n".join(lines)

        # Should use WARNING as default severity
        assert "severity: WARNING" in yaml_text


class TestJsonToYamlCLI:
    """Integration tests for CLI usage."""

    def test_convert_file_to_file(self) -> None:
        """Full roundtrip: write JSON file → read → convert → write YAML."""
        # Create temp input file
        input_data = {
            "version": "0.1.0",
            "rules": [
                {
                    "id": "test-001",
                    "languages": ["python"],
                    "message": "Test rule",
                    "severity": "ERROR",
                    "patterns": [{"pattern": "test"}],
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "rules.json"
            output_file = Path(tmpdir) / "rules.yml"

            # Write JSON input
            input_file.write_text(json.dumps(input_data), encoding="utf-8")

            # Convert
            yaml_output = json_to_semgrep_yaml(input_data)
            output_file.write_text(yaml_output, encoding="utf-8")

            # Verify output exists and has expected content
            assert output_file.exists()
            yaml_content = output_file.read_text(encoding="utf-8")
            assert "id: test-001" in yaml_content
            assert "rules:" in yaml_content
