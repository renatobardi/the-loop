"""Unit tests for IncidentAttachment domain model."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from src.domain.models import AttachmentExtractionStatus, AttachmentType, IncidentAttachment


def _make_attachment(**overrides: object) -> IncidentAttachment:
    now = datetime.now(timezone.utc)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "incident_id": uuid4(),
        "filename": "postmortem.pdf",
        "mime_type": "application/pdf",
        "file_size_bytes": 1024,
        "gcs_bucket": "loop-prod-attachments",
        "gcs_object_path": "tenants/t1/incidents/i1/postmortem.pdf",
        "attachment_type": AttachmentType.POSTMORTEM_DOC,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return IncidentAttachment(**defaults)  # type: ignore[arg-type]


def test_create_attachment_defaults_extraction_pending() -> None:
    a = _make_attachment()
    assert a.extraction_status == AttachmentExtractionStatus.PENDING
    assert a.content_text is None
    assert a.uploaded_by is None


def test_zero_file_size_rejected() -> None:
    with pytest.raises(ValueError, match="> 0"):
        _make_attachment(file_size_bytes=0)


def test_negative_file_size_rejected() -> None:
    with pytest.raises(ValueError, match="> 0"):
        _make_attachment(file_size_bytes=-100)


def test_frozen_model() -> None:
    a = _make_attachment()
    with pytest.raises(Exception):
        a.filename = "changed"  # type: ignore[misc]
