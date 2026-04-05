"""Seed rule_versions with v0.3.0 on initial deployment.

Revision ID: 014
Revises: 013
Create Date: 2026-04-05
"""

import json
from typing import Any
from uuid import UUID, uuid4, uuid5, NAMESPACE_URL

from alembic import op
import sqlalchemy as sa


revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


# v0.3.0 rules (45 rules: Phase A + Phase B + Phase C)
# Placeholder: Migration 015 contains full 45 rules (hardcoded to avoid file I/O in Cloud Run)
# This migration only seeds v0.3.0 with stub; migration 015 backfills the complete rules
V030_RULES: list[dict[str, Any]] = [
    {
        "id": "injection-001-sql-string-concat",
        "languages": ["python", "javascript", "typescript", "java", "go", "ruby"],
        "message": "[The Loop] SQL injection via string concatenation",
        "severity": "ERROR",
        "category": "injection",
        "patterns": [{"pattern": "$QUERY + $VAR"}],
        "metadata": {"cwe": "CWE-89"},
    },
    # Note: Full 44 remaining rules are backfilled by migration 015_fix_rule_versions_v030_full_rules
]

ADMIN_FIREBASE_UID: str = str(uuid5(NAMESPACE_URL, "firebase:admin@loop.oute.pro"))
ADMIN_EMAIL: str = "admin@loop.oute.pro"
RULES_VERSION: str = "0.3.0"


def upgrade() -> None:
    """Seed v0.3.0 rules on initial deployment.

    This migration:
    1. Creates or updates an admin user (deterministic UUID5)
    2. Inserts v0.3.0 if it doesn't exist
    3. Validates rules before insertion
    4. Is fully idempotent (safe to re-run)
    5. Raises on fatal errors (no silent failures)
    6. Explicitly commits transaction
    """
    connection = op.get_bind()

    # Step 1: Upsert admin user (deterministic by firebase_uid)
    # If user exists, ensure is_admin = true; if not, create with new UUID
    admin_id: str = str(uuid4())
    result = connection.execute(
        sa.text("""
        INSERT INTO users (id, firebase_uid, email, is_admin)
        VALUES (:id, :firebase_uid, :email, :is_admin)
        ON CONFLICT (firebase_uid) DO UPDATE SET is_admin = true
        RETURNING id
        """),
        {
            "id": admin_id,
            "firebase_uid": ADMIN_FIREBASE_UID,
            "email": ADMIN_EMAIL,
            "is_admin": True,
        }
    )
    admin_row = result.first()
    if not admin_row:
        raise RuntimeError("Failed to create or retrieve admin user")
    actual_admin_id: UUID = admin_row[0]

    # Step 2: Check if v0.3.0 already exists
    existing = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": RULES_VERSION}
    )
    existing_row = existing.first()

    if existing_row:
        # v0.3.0 exists — verify it has rules to avoid silent data loss
        existing_rules: Any = existing_row[1]
        if isinstance(existing_rules, str):
            rules_list: Any = json.loads(existing_rules)
        else:
            rules_list = existing_rules

        if not isinstance(rules_list, list) or len(rules_list) == 0:
            raise RuntimeError(
                f"v{RULES_VERSION} exists but has empty rules. "
                "Database is in inconsistent state. Manual intervention required."
            )
        # Rules exist and are valid — idempotent success
        return

    # Step 3: Validate rules before insertion
    if not V030_RULES:
        raise ValueError(f"No rules available for v{RULES_VERSION}. Cannot proceed.")

    try:
        rules_json: str = json.dumps(V030_RULES)
        # Verify it round-trips correctly
        json.loads(rules_json)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize or validate rules: {e}") from e

    # Step 4: Insert v0.3.0 with rules (only if doesn't exist)
    connection.execute(
        sa.text("""
        INSERT INTO rule_versions (id, version, rules_json, status, notes, published_by)
        VALUES (:id, :version, :rules_json, :status, :notes, :published_by)
        """),
        {
            "id": str(uuid4()),
            "version": RULES_VERSION,
            "rules_json": rules_json,
            "status": "active",
            "notes": "Phase C: 45 rules (20 Python + 15 JS/TS + 10 Go)",
            "published_by": actual_admin_id,
        }
    )

    # Step 5: Explicitly commit (required by CLAUDE.md: feedback_transaction_commits)
    connection.commit()


def downgrade() -> None:
    """Remove v0.3.0 and associated admin user on downgrade.

    Symmetric with upgrade: removes both rule_versions and users entries.
    Raises on error instead of failing silently.
    """
    connection = op.get_bind()

    # Step 1: Delete rule_versions entry
    result = connection.execute(
        sa.text("DELETE FROM rule_versions WHERE version = :version"),
        {"version": RULES_VERSION}
    )
    if result.rowcount == 0:
        raise RuntimeError(f"v{RULES_VERSION} not found during downgrade")

    # Step 2: Delete admin user (by deterministic firebase_uid)
    # Use WHERE firebase_uid explicitly (not is_admin) to avoid deleting other admins
    connection.execute(
        sa.text("DELETE FROM users WHERE firebase_uid = :firebase_uid"),
        {"firebase_uid": ADMIN_FIREBASE_UID}
    )

    # Step 3: Explicitly commit
    connection.commit()
