"""add is_admin to users

Revision ID: 011
Revises: 010
Create Date: 2026-04-04
"""

import sqlalchemy as sa
from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
    )
    # To grant admin to yourself: UPDATE users SET is_admin = TRUE WHERE email = 'your@email.com'


def downgrade() -> None:
    op.drop_column("users", "is_admin")
