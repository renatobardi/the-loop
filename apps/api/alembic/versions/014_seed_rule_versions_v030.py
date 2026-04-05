"""Seed rule_versions with v0.3.0 on initial deployment.

Revision ID: 014
Revises: 013
Create Date: 2026-04-05
"""

import json
import uuid
from uuid import NAMESPACE_URL
import yaml
from alembic import op
import sqlalchemy as sa


revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Insert v0.3.0 rules if they don't exist."""

    # Read rules from YAML backup
    import os
    import pathlib

    # Workaround: search for .semgrep directory by walking up from current location
    current = pathlib.Path.cwd()
    rules_file = None

    for parent in [current] + list(current.parents):
        candidate = parent / ".semgrep" / "theloop-rules.yml.bak"
        if candidate.exists():
            rules_file = candidate
            break

    # Fallback: hardcoded path for GCP Cloud Run
    if not rules_file:
        hardcoded = pathlib.Path("/Users/bardi/Projetos/the-loop/.semgrep/theloop-rules.yml.bak")
        if hardcoded.exists():
            rules_file = hardcoded

    rules = []
    if rules_file:
        try:
            with open(rules_file) as f:
                data = yaml.safe_load(f)
            rules = data.get("rules", [])
            print(f"✅ Loaded {len(rules)} rules from {rules_file}")
        except Exception as e:
            print(f"⚠️  Error reading rules: {e}")
    else:
        print("⚠️  No rules to seed (.semgrep/theloop-rules.yml.bak not found)")
        return

    if not rules:
        print("⚠️  No rules to seed (file not found in any path)")
        return

    # Create admin user if not exists
    admin_uid = str(uuid.uuid5(NAMESPACE_URL, "firebase:admin@loop.oute.pro"))

    # Get or create admin user
    connection = op.get_bind()

    # Insert admin user if not exists
    connection.execute(
        sa.text("""
        INSERT INTO users (id, firebase_uid, email, is_admin)
        VALUES (:id, :firebase_uid, :email, :is_admin)
        ON CONFLICT (firebase_uid) DO NOTHING
        """),
        {
            "id": str(uuid.uuid4()),
            "firebase_uid": admin_uid,
            "email": "admin@loop.oute.pro",
            "is_admin": True,
        }
    )

    # Get admin ID
    result = connection.execute(
        sa.text("SELECT id FROM users WHERE is_admin = true LIMIT 1")
    )
    admin_row = result.first()
    admin_id = admin_row[0] if admin_row else str(uuid.uuid4())

    # Insert v0.3.0 if not exists
    connection.execute(
        sa.text("""
        INSERT INTO rule_versions (id, version, rules_json, status, notes, published_by)
        VALUES (:id, :version, :rules_json, :status, :notes, :published_by)
        ON CONFLICT (version) DO NOTHING
        """),
        {
            "id": str(uuid.uuid4()),
            "version": "0.3.0",
            "rules_json": json.dumps(rules),
            "status": "active",
            "notes": "Phase C: 45 rules (20 Python + 15 JS/TS + 10 Go)",
            "published_by": admin_id,
        }
    )

    print(f"✅ Seeded v0.3.0 with {len(rules)} rules")


def downgrade() -> None:
    """Remove v0.3.0 on downgrade."""
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM rule_versions WHERE version = '0.3.0'")
    )
