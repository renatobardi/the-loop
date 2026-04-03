"""Unit tests for IncidentService — all I/O mocked via AsyncMock."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from src.domain.exceptions import IncidentHasActiveRuleError, IncidentNotFoundError
from src.domain.models import Category, Incident, PostmortemStatus, Severity
from src.domain.services import IncidentService

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")


def _make_incident(**kwargs: object) -> Incident:
    defaults: dict[str, object] = {
        "id": uuid4(),
        "title": "SQL injection via raw query",
        "category": Category.INJECTION,
        "severity": Severity.HIGH,
        "anti_pattern": "Raw SQL string interpolation",
        "remediation": "Use parameterised queries",
        "version": 1,
        "created_at": _NOW,
        "updated_at": _NOW,
        "created_by": _USER,
    }
    defaults.update(kwargs)
    return Incident(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(repo: AsyncMock) -> IncidentService:
    return IncidentService(repo)


async def test_create_delegates_to_repo(service: IncidentService, repo: AsyncMock) -> None:
    incident = _make_incident()
    repo.create.return_value = incident

    result = await service.create(
        title="SQL injection via raw query",
        category=Category.INJECTION,
        severity=Severity.HIGH,
        anti_pattern="Raw SQL string interpolation",
        remediation="Use parameterised queries",
        created_by=_USER,
    )

    repo.create.assert_awaited_once()
    assert result is incident


async def test_create_with_optional_fields(service: IncidentService, repo: AsyncMock) -> None:
    incident = _make_incident(source_url="https://example.com", tags=["python"])
    repo.create.return_value = incident

    result = await service.create(
        title="SQL injection via raw query",
        category=Category.INJECTION,
        severity=Severity.HIGH,
        anti_pattern="Raw SQL",
        remediation="Parameterise",
        created_by=_USER,
        source_url="https://example.com",
        tags=["python"],
        affected_languages=["python"],
    )

    assert result.source_url == "https://example.com"


async def test_get_by_id_found(service: IncidentService, repo: AsyncMock) -> None:
    incident = _make_incident()
    repo.get_by_id.return_value = incident

    result = await service.get_by_id(incident.id)

    assert result is incident


async def test_get_by_id_not_found(service: IncidentService, repo: AsyncMock) -> None:
    repo.get_by_id.return_value = None

    with pytest.raises(IncidentNotFoundError):
        await service.get_by_id(uuid4())


async def test_update_not_found(service: IncidentService, repo: AsyncMock) -> None:
    repo.get_by_id.return_value = None

    with pytest.raises(IncidentNotFoundError):
        await service.update(uuid4(), 1, title="New title")


async def test_update_category_change_with_active_rule(
    service: IncidentService, repo: AsyncMock
) -> None:
    incident = _make_incident(semgrep_rule_id="injection-001", category=Category.INJECTION)
    repo.get_by_id.return_value = incident

    with pytest.raises(IncidentHasActiveRuleError):
        await service.update(incident.id, 1, category=Category.RACE_CONDITION)


async def test_update_same_category_with_active_rule_ok(
    service: IncidentService, repo: AsyncMock
) -> None:
    incident = _make_incident(semgrep_rule_id="injection-001", category=Category.INJECTION)
    updated = _make_incident(
        semgrep_rule_id="injection-001", category=Category.INJECTION, title="Updated"
    )
    repo.get_by_id.return_value = incident
    repo.update.return_value = updated

    result = await service.update(incident.id, 1, category=Category.INJECTION, title="Updated")

    assert result is updated


async def test_update_success(service: IncidentService, repo: AsyncMock) -> None:
    incident = _make_incident()
    updated = _make_incident(title="Updated title", version=2)
    repo.get_by_id.return_value = incident
    repo.update.return_value = updated

    result = await service.update(incident.id, 1, title="Updated title")

    repo.update.assert_awaited_once()
    assert result is updated


async def test_soft_delete_not_found(service: IncidentService, repo: AsyncMock) -> None:
    repo.get_by_id.return_value = None

    with pytest.raises(IncidentNotFoundError):
        await service.soft_delete(uuid4())


async def test_soft_delete_with_active_rule(service: IncidentService, repo: AsyncMock) -> None:
    incident = _make_incident(semgrep_rule_id="injection-001")
    repo.get_by_id.return_value = incident

    with pytest.raises(IncidentHasActiveRuleError):
        await service.soft_delete(incident.id)


async def test_soft_delete_success(service: IncidentService, repo: AsyncMock) -> None:
    incident = _make_incident()
    repo.get_by_id.return_value = incident

    await service.soft_delete(incident.id)

    repo.soft_delete.assert_awaited_once_with(incident.id)


async def test_list_incidents_delegates_to_repo(
    service: IncidentService, repo: AsyncMock
) -> None:
    incidents = [_make_incident(), _make_incident()]
    repo.list_incidents.return_value = (incidents, 2)

    result_items, total = await service.list_incidents(
        page=1, per_page=20, category=Category.INJECTION
    )

    assert result_items is incidents
    assert total == 2


async def test_list_incidents_clamps_pagination(
    service: IncidentService, repo: AsyncMock
) -> None:
    repo.list_incidents.return_value = ([], 0)

    await service.list_incidents(page=0, per_page=200)

    call_kwargs = repo.list_incidents.call_args.kwargs
    assert call_kwargs["page"] == 1
    assert call_kwargs["per_page"] == 100


# T024 — auto-populate postmortem_published_at on PUBLISHED transition


async def test_update_published_status_auto_populates_published_at(
    service: IncidentService, repo: AsyncMock
) -> None:
    incident = _make_incident(postmortem_status=PostmortemStatus.DRAFT)
    repo.get_by_id.return_value = incident
    repo.update.return_value = incident

    await service.update(incident.id, 1, postmortem_status=PostmortemStatus.PUBLISHED)

    call_args = repo.update.call_args
    updated: Incident = call_args[0][0]
    assert updated.postmortem_status == PostmortemStatus.PUBLISHED
    assert updated.postmortem_published_at is not None


async def test_update_published_at_not_overwritten_when_already_set(
    service: IncidentService, repo: AsyncMock
) -> None:
    original_ts = datetime(2025, 3, 1, tzinfo=UTC)
    incident = _make_incident(
        postmortem_status=PostmortemStatus.PUBLISHED,
        postmortem_published_at=original_ts,
    )
    repo.get_by_id.return_value = incident
    repo.update.return_value = incident

    await service.update(incident.id, 1, postmortem_status=PostmortemStatus.PUBLISHED)

    call_args = repo.update.call_args
    updated: Incident = call_args[0][0]
    assert updated.postmortem_published_at == original_ts


async def test_update_non_published_status_does_not_set_published_at(
    service: IncidentService, repo: AsyncMock
) -> None:
    incident = _make_incident(postmortem_status=PostmortemStatus.DRAFT)
    repo.get_by_id.return_value = incident
    repo.update.return_value = incident

    await service.update(incident.id, 1, postmortem_status=PostmortemStatus.IN_REVIEW)

    call_args = repo.update.call_args
    updated: Incident = call_args[0][0]
    assert updated.postmortem_published_at is None
