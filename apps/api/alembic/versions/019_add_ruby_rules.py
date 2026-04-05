"""Add 10 Ruby rules to v0.4.0 (Spec-017 Phase 5)

Revision ID: 019
Revises: 018
Create Date: 2026-04-05

"""

import json
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add 10 Ruby rules to v0.4.0, bringing total from 85 to 95 rules."""
    connection = op.get_bind()

    existing_check = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_row = existing_check.first()

    if existing_row:
        existing_rules = (
            json.loads(existing_row[1])
            if isinstance(existing_row[1], str)
            else existing_row[1]
        )
        rule_count = len(existing_rules) if isinstance(existing_rules, list) else 0
        if rule_count >= 95:
            return
        if rule_count not in (45, 60, 75, 85):
            raise RuntimeError(
                f"Version v0.4.0 exists with {rule_count} rules; expected intermediate state. "
                "Database state is inconsistent. Manual review required."
            )

    RUBY_RULES = [
        {"id": "ruby-injection-001", "languages": ["ruby"], "message": "[The Loop] SQL injection via string concatenation in ActiveRecord", "severity": "ERROR", "patterns": [{"pattern-either": ["ActiveRecord::Base.connection.execute(\"...\" + $INPUT)", "User.find_by_sql(\"...\" + $INPUT)"]}], "metadata": {"category": "injection", "cwe": "CWE-89"}},
        {"id": "ruby-injection-002", "languages": ["ruby"], "message": "[The Loop] Command injection via backticks or system() with user input", "severity": "ERROR", "patterns": [{"pattern-either": ["`$CMD`", "system($CMD)", "exec($CMD)"]}], "metadata": {"category": "injection", "cwe": "CWE-78"}},
        {"id": "ruby-injection-003", "languages": ["ruby"], "message": "[The Loop] Unsafe evaluation of user-supplied code", "severity": "ERROR", "patterns": [{"pattern-either": ["eval($INPUT)", "instance_eval($INPUT)", "class_eval($INPUT)"]}], "metadata": {"category": "injection", "cwe": "CWE-94"}},
        {"id": "ruby-crypto-001", "languages": ["ruby"], "message": "[The Loop] Weak hash algorithm (MD5 or SHA1) detected", "severity": "WARNING", "patterns": [{"pattern-either": ["Digest::MD5.digest(...)", "Digest::SHA1.digest(...)"]}], "metadata": {"category": "crypto", "cwe": "CWE-327"}},
        {"id": "ruby-crypto-002", "languages": ["ruby"], "message": "[The Loop] Weak random for security-sensitive operations", "severity": "ERROR", "patterns": [{"pattern": "SecureRandom.random_bytes($N) if rand() > 0.5"}], "metadata": {"category": "crypto", "cwe": "CWE-338"}},
        {"id": "ruby-security-001", "languages": ["ruby"], "message": "[The Loop] Hardcoded API key or credential in source code", "severity": "ERROR", "patterns": [{"pattern-regex": "\\$(api_key|password|secret)\\s*=\\s*['\"][^'\"]+['\"]"}], "metadata": {"category": "security", "cwe": "CWE-798"}},
        {"id": "ruby-security-002", "languages": ["ruby"], "message": "[The Loop] Mass assignment vulnerability — all params sent to model", "severity": "WARNING", "patterns": [{"pattern": "User.create(params)"}], "metadata": {"category": "security", "cwe": "CWE-434"}},
        {"id": "ruby-security-003", "languages": ["ruby"], "message": "[The Loop] Unsafe use of YAML.load() — use YAML.safe_load()", "severity": "ERROR", "patterns": [{"pattern": "YAML.load($INPUT)"}], "metadata": {"category": "security", "cwe": "CWE-502"}},
        {"id": "ruby-error-001", "languages": ["ruby"], "message": "[The Loop] Bare rescue catches StandardError and masks bugs", "severity": "WARNING", "patterns": [{"pattern-regex": "rescue\\s*$"}], "metadata": {"category": "error-handling"}},
        {"id": "ruby-config-001", "languages": ["ruby"], "message": "[The Loop] Rails.env == 'production' check for toggling security (missing in dev)", "severity": "WARNING", "patterns": [{"pattern-regex": "skip_.*if.*Rails\\.env.*production"}], "metadata": {"category": "config"}},
    ]

    FULL_RULES_COUNT = 95
    RUBY_RULES_COUNT = len(RUBY_RULES)
    if RUBY_RULES_COUNT != 10:
        raise RuntimeError(f"Expected 10 Ruby rules; found {RUBY_RULES_COUNT}. Data integrity check failed.")

    existing_result = connection.execute(
        sa.text("SELECT rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_data = existing_result.first()
    if not existing_data:
        raise RuntimeError("v0.4.0 does not exist. Run migration 018 first.")

    existing_rules = json.loads(existing_data[0]) if isinstance(existing_data[0], str) else existing_data[0]
    merged_rules = existing_rules + RUBY_RULES

    if len(merged_rules) != FULL_RULES_COUNT:
        raise RuntimeError(f"Rule count mismatch: expected {FULL_RULES_COUNT}, got {len(merged_rules)}")

    connection.execute(
        sa.text("UPDATE rule_versions SET rules_json = :json WHERE version = :version"),
        {"json": json.dumps(merged_rules), "version": "0.4.0"},
    )
    connection.commit()


def downgrade() -> None:
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_row = result.first()
    if existing_row:
        existing_rules = json.loads(existing_row[1]) if isinstance(existing_row[1], str) else existing_row[1]
        filtered_rules = [r for r in existing_rules if not r.get("id", "").startswith("ruby-")]
        if len(filtered_rules) >= 85:
            connection.execute(
                sa.text("UPDATE rule_versions SET rules_json = :json WHERE version = :version"),
                {"json": json.dumps(filtered_rules), "version": "0.4.0"},
            )
            connection.commit()
