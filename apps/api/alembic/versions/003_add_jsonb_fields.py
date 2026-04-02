"""Add JSONB enrichment fields to incidents for RAG quality.

Revision ID: 003
Revises: 002
Create Date: 2026-04-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("incidents", sa.Column("raw_content", JSONB, nullable=True))
    op.add_column("incidents", sa.Column("tech_context", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("incidents", "tech_context")
    op.drop_column("incidents", "raw_content")
