"""Unit tests for ScanService — domain logic only, repos mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from src.domain.models import ApiKey, Scan
from src.domain.services import ScanService

_OWNER_ID = UUID("00000000-0000-0000-0000-000000000001")
_KEY_ID = UUID("00000000-0000-0000-0000-000000000002")
_SCAN_ID = UUID("00000000-0000-0000-0000-000000000003")
_NOW = datetime(2026, 4, 4, tzinfo=UTC)


def _make_api_key(**kwargs: object) -> ApiKey:
    defaults: dict[str, object] = {
        "id": _KEY_ID,
        "owner_id": _OWNER_ID,
        "name": "ci-key",
        "prefix": "tlp_abc",
        "last_used_at": None,
        "revoked_at": None,
        "created_at": _NOW,
    }
    defaults.update(kwargs)
    return ApiKey(**defaults)  # type: ignore[arg-type]


def _make_scan(**kwargs: object) -> Scan:
    defaults: dict[str, object] = {
        "id": _SCAN_ID,
        "api_key_id": _KEY_ID,
        "repository": "owner/repo",
        "branch": "main",
        "pr_number": None,
        "rules_version": "0.2.0",
        "findings_count": 2,
        "errors_count": 1,
        "warnings_count": 1,
        "duration_ms": 4500,
        "created_at": _NOW,
    }
    defaults.update(kwargs)
    return Scan(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_api_key_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repo: AsyncMock, mock_api_key_repo: AsyncMock) -> ScanService:
    return ScanService(repo=mock_repo, api_key_repo=mock_api_key_repo)


async def test_register_scan(service: ScanService, mock_repo: AsyncMock) -> None:
    """register() delegates to repo.create_with_findings and returns the Scan."""
    api_key = _make_api_key()
    scan = _make_scan()
    mock_repo.create_with_findings.return_value = scan

    findings: list[dict[str, str | int]] = [
        {"rule_id": "injection-001", "file_path": "app.py", "line_number": 42, "severity": "ERROR"}
    ]
    result = await service.register(
        api_key=api_key,
        repository="owner/repo",
        branch="main",
        pr_number=None,
        rules_version="0.2.0",
        findings_count=1,
        errors_count=1,
        warnings_count=0,
        duration_ms=3000,
        findings=findings,
    )

    assert result == scan
    mock_repo.create_with_findings.assert_called_once_with(
        api_key_id=_KEY_ID,
        repository="owner/repo",
        branch="main",
        pr_number=None,
        rules_version="0.2.0",
        findings_count=1,
        errors_count=1,
        warnings_count=0,
        duration_ms=3000,
        findings=findings,
    )


async def test_register_with_pr_number(service: ScanService, mock_repo: AsyncMock) -> None:
    """register() correctly passes pr_number to repo."""
    api_key = _make_api_key()
    scan = _make_scan(pr_number=42)
    mock_repo.create_with_findings.return_value = scan

    result = await service.register(
        api_key=api_key,
        repository="owner/repo",
        branch="feat/my-feature",
        pr_number=42,
        rules_version="0.1.0",
        findings_count=0,
        errors_count=0,
        warnings_count=0,
        duration_ms=1000,
        findings=[],
    )

    assert result.pr_number == 42


async def test_list_by_user(service: ScanService, mock_repo: AsyncMock) -> None:
    """list_by_user() delegates to repo.list_by_owner."""
    scans = [_make_scan(), _make_scan(id=UUID("00000000-0000-0000-0000-000000000009"))]
    mock_repo.list_by_owner.return_value = scans

    result = await service.list_by_user(owner_id=_OWNER_ID)

    assert result == scans
    mock_repo.list_by_owner.assert_called_once_with(_OWNER_ID)


async def test_get_summary(service: ScanService, mock_repo: AsyncMock) -> None:
    """get_summary() delegates to repo.get_summary."""
    summary: dict[str, object] = {
        "total_scans": 10,
        "total_findings": 25,
        "scans_by_week": [{"week": "2026-W14", "count": 3, "findings": 7}],
        "top_rules": [{"rule_id": "injection-001", "count": 5}],
    }
    mock_repo.get_summary.return_value = summary

    result = await service.get_summary(owner_id=_OWNER_ID)

    assert result == summary
    mock_repo.get_summary.assert_called_once_with(_OWNER_ID)


async def test_register_empty_findings(service: ScanService, mock_repo: AsyncMock) -> None:
    """register() handles empty findings list (no-error scan)."""
    api_key = _make_api_key()
    scan = _make_scan(findings_count=0, errors_count=0, warnings_count=0)
    mock_repo.create_with_findings.return_value = scan

    result = await service.register(
        api_key=api_key,
        repository="owner/repo",
        branch="main",
        pr_number=None,
        rules_version="0.2.0",
        findings_count=0,
        errors_count=0,
        warnings_count=0,
        duration_ms=500,
        findings=[],
    )

    assert result.findings_count == 0
    assert result.errors_count == 0
