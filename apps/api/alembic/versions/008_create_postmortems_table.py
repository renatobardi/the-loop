"""Create postmortems table for Phase C incident knowledge capture.

Revision ID: 008
Revises: 007
Create Date: 2026-04-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create postmortems table
    op.create_table(
        "postmortems",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("incident_id", sa.UUID(), nullable=False),
        sa.Column("root_cause_category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("suggested_pattern", sa.String(1000), nullable=True),
        sa.Column("team_responsible", sa.String(255), nullable=False),
        sa.Column("severity_for_rule", sa.String(50), nullable=False),
        sa.Column("related_rule_id", sa.String(100), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("incident_id", name="uc_one_postmortem_per_incident"),
        # Constraints: description length validation
        sa.CheckConstraint("LENGTH(description) >= 20", name="ck_description_min_length"),
        sa.CheckConstraint("LENGTH(description) <= 2000", name="ck_description_max_length"),
    )

    # Create indexes for query performance
    op.create_index("idx_postmortems_category", "postmortems", ["root_cause_category"])
    op.create_index("idx_postmortems_team", "postmortems", ["team_responsible"])
    op.create_index("idx_postmortems_created_at", "postmortems", ["created_at"])
    op.create_index("idx_postmortems_incident_id", "postmortems", ["incident_id"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_postmortems_incident_id", table_name="postmortems")
    op.drop_index("idx_postmortems_created_at", table_name="postmortems")
    op.drop_index("idx_postmortems_team", table_name="postmortems")
    op.drop_index("idx_postmortems_category", table_name="postmortems")

    # Drop table
    op.drop_table("postmortems")
