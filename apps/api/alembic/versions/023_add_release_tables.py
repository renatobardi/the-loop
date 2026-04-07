"""Add Release and ReleaseNotificationStatus tables for Product Releases Notification (Spec-022)

Revision ID: 023
Revises: 022
Create Date: 2026-04-06

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "023"
down_revision = "022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Release table
    op.create_table(
        "releases",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("published_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("changelog_html", sa.Text(), nullable=True),
        sa.Column("breaking_changes_flag", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("documentation_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_releases"),
        sa.UniqueConstraint("version", name="uq_releases_version"),
    )
    op.create_index("ix_releases_published_date", "releases", ["published_date"], unique=False)

    # Create ReleaseNotificationStatus table
    op.create_table(
        "release_notification_status",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("release_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_release_notification_status"),
        sa.ForeignKeyConstraint(["release_id"], ["releases.id"], name="fk_release_notification_status_release_id"),
        sa.UniqueConstraint("release_id", "user_id", name="uq_release_notification_status_release_user"),
    )
    op.create_index("ix_release_notification_status_user_id", "release_notification_status", ["user_id"], unique=False)
    op.create_index("ix_release_notification_status_read_at", "release_notification_status", ["read_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_release_notification_status_read_at", table_name="release_notification_status")
    op.drop_index("ix_release_notification_status_user_id", table_name="release_notification_status")
    op.drop_table("release_notification_status")
    op.drop_index("ix_releases_published_date", table_name="releases")
    op.drop_table("releases")
