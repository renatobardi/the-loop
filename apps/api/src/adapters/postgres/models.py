"""SQLAlchemy ORM model for the incidents table."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]
from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IncidentRow(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    failure_mode: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    affected_languages: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    anti_pattern: Mapped[str] = mapped_column(Text, nullable=False)
    code_example: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation: Mapped[str] = mapped_column(Text, nullable=False)
    static_rule_possible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    semgrep_rule_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    embedding = mapped_column(Vector(768), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
