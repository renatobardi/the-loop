"""Add 8 Rust rules to v0.4.0 (Spec-017 Phase 7A)

Revision ID: 021
Revises: 020
Create Date: 2026-04-05

"""

import json
from alembic import op
import sqlalchemy as sa

revision = "021"
down_revision = "020"
branch_labels = None
depends_on = None

def upgrade() -> None:
    connection = op.get_bind()
    existing_check = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_row = existing_check.first()
    if existing_row:
        existing_rules = json.loads(existing_row[1]) if isinstance(existing_row[1], str) else existing_row[1]
        rule_count = len(existing_rules) if isinstance(existing_rules, list) else 0
        if rule_count >= 113:
            return
        if rule_count not in (45, 60, 75, 85, 95, 105):
            raise RuntimeError(f"Version v0.4.0 exists with {rule_count} rules; expected intermediate state.")

    RUST_RULES = [
        {"id": "rust-injection-001", "languages": ["rust"], "message": "[The Loop] SQL injection via string formatting in sqlx or rusqlite", "severity": "ERROR", "patterns": [{"pattern-either": ["sqlx::query($FORMAT + $INPUT)", "conn.execute(format!(\"SELECT ... WHERE {}\", $INPUT))"]}], "metadata": {"category": "injection", "cwe": "CWE-89"}},
        {"id": "rust-injection-002", "languages": ["rust"], "message": "[The Loop] Command injection via Command::new() with unsanitized args", "severity": "ERROR", "patterns": [{"pattern": "Command::new($CMD).arg($INPUT).output()"}], "metadata": {"category": "injection", "cwe": "CWE-78"}},
        {"id": "rust-crypto-001", "languages": ["rust"], "message": "[The Loop] Use of weak RNG (rand::random) for cryptography", "severity": "WARNING", "patterns": [{"pattern": "rand::random()"}], "metadata": {"category": "crypto", "cwe": "CWE-338"}},
        {"id": "rust-crypto-002", "languages": ["rust"], "message": "[The Loop] Hardcoded cryptographic key in source code", "severity": "ERROR", "patterns": [{"pattern-regex": "const\\s+(KEY|SECRET|PASSWORD)\\s*=\\s*b?['\"][^'\"]+['\"]"}], "metadata": {"category": "crypto", "cwe": "CWE-798"}},
        {"id": "rust-security-001", "languages": ["rust"], "message": "[The Loop] Unsafe block without justification — potential memory safety issue", "severity": "WARNING", "patterns": [{"pattern": "unsafe { ... }"}], "metadata": {"category": "security", "cwe": "CWE-416"}},
        {"id": "rust-security-002", "languages": ["rust"], "message": "[The Loop] panic!() in library code — use Result instead", "severity": "WARNING", "patterns": [{"pattern": "panic!(...)"}], "metadata": {"category": "security"}},
        {"id": "rust-error-001", "languages": ["rust"], "message": "[The Loop] unwrap() called on Result without context — prefer ? operator", "severity": "WARNING", "patterns": [{"pattern-regex": "unwrap()"}], "metadata": {"category": "error-handling"}},
    ]

    # Only 8 Rust rules (not 10)
    FULL_RULES_COUNT = 113  # 105 + 8
    if len(RUST_RULES) != 8:
        raise RuntimeError(f"Expected 8 Rust rules; found {len(RUST_RULES)}.")

    existing_result = connection.execute(
        sa.text("SELECT rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_data = existing_result.first()
    if not existing_data:
        raise RuntimeError("v0.4.0 does not exist.")

    existing_rules = json.loads(existing_data[0]) if isinstance(existing_data[0], str) else existing_data[0]
    merged_rules = existing_rules + RUST_RULES

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
        filtered_rules = [r for r in existing_rules if not r.get("id", "").startswith("rust-")]
        if len(filtered_rules) >= 105:
            connection.execute(
                sa.text("UPDATE rule_versions SET rules_json = :json WHERE version = :version"),
                {"json": json.dumps(filtered_rules), "version": "0.4.0"},
            )
            connection.commit()
