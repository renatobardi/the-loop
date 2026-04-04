"""Add analytics indexes for Phase C.2 dashboard queries.

Revision ID: 009
Revises: 008
Create Date: 2026-04-03
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # T002: Index for category analytics (Q1 — by category with period filter)
    op.create_index(
        "idx_postmortems_created_category",
        "postmortems",
        ["created_at", "root_cause_category"],
        postgresql_ops={"created_at": "DESC"},
    )

    # T003: Index for team analytics (by team with period filter)
    op.create_index(
        "idx_postmortems_team_created",
        "postmortems",
        ["team_responsible", "created_at"],
        postgresql_ops={"created_at": "DESC"},
    )

    # T004: Index for resolution time calculations (JOIN incidents on resolved_at)
    op.create_index(
        "idx_incidents_resolved_created",
        "incidents",
        ["resolved_at", "created_at"],
        postgresql_ops={"created_at": "DESC"},
    )

    # T005 deferred (Spec-015): idx_timeline_events_rule
    # Not needed until rule_block events exist


def downgrade() -> None:
    op.drop_index("idx_incidents_resolved_created", table_name="incidents")
    op.drop_index("idx_postmortems_team_created", table_name="postmortems")
    op.drop_index("idx_postmortems_created_category", table_name="postmortems")
