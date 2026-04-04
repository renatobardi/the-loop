"""Unit tests for ApiKeyService — domain logic only, repo mocked."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from src.domain.exceptions import ApiKeyInvalidError, ApiKeyRevokedError
from src.domain.models import ApiKey
from src.domain.services import ApiKeyService

_OWNER_ID = UUID("00000000-0000-0000-0000-000000000001")
_KEY_ID = UUID("00000000-0000-0000-0000-000000000002")
_NOW = datetime(2026, 4, 4, tzinfo=UTC)


def _make_api_key(**kwargs: object) -> ApiKey:
    defaults: dict[str, object] = {
        "id": _KEY_ID,
        "owner_id": _OWNER_ID,
        "name": "test-key",
        "prefix": "tlp_abc",
        "last_used_at": None,
        "revoked_at": None,
        "created_at": _NOW,
    }
    defaults.update(kwargs)
    return ApiKey(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repo: AsyncMock) -> ApiKeyService:
    return ApiKeyService(repo=mock_repo)


async def test_create_token_format(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    """create() generates a tlp_ prefixed token and stores its SHA-256 hash."""
    api_key = _make_api_key()
    mock_repo.create.return_value = api_key

    raw_token, result = await service.create(owner_id=_OWNER_ID, name="my-key")

    assert raw_token.startswith("tlp_")
    assert len(raw_token) == 4 + 64  # "tlp_" + 32 hex bytes = 68 chars
    assert result == api_key

    # The hash stored must be SHA-256 of the raw token
    expected_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    call_args = mock_repo.create.call_args
    # positional args: (owner_id, name, key_hash, prefix)
    args = call_args.args
    assert args[2] == expected_hash  # key_hash
    assert args[3] == raw_token[:7]  # prefix


async def test_create_prefix_is_first_7_chars(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    api_key = _make_api_key()
    mock_repo.create.return_value = api_key

    raw_token, _ = await service.create(owner_id=_OWNER_ID, name="key")

    call_args = mock_repo.create.call_args
    args = call_args.args
    assert args[3] == raw_token[:7]  # prefix
    assert args[3].startswith("tlp_")


async def test_validate_valid_token(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    """validate() returns ApiKey and calls mark_used for valid token."""
    api_key = _make_api_key()
    mock_repo.get_by_hash.return_value = api_key
    mock_repo.mark_used.return_value = None

    result = await service.validate("tlp_valid_token_xxx")

    assert result == api_key
    mock_repo.mark_used.assert_called_once_with(_KEY_ID)


async def test_validate_invalid_token_raises(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    """validate() raises ApiKeyInvalidError when token not found in DB."""
    mock_repo.get_by_hash.return_value = None

    with pytest.raises(ApiKeyInvalidError):
        await service.validate("tlp_nonexistent")


async def test_validate_revoked_token_raises(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    """validate() raises ApiKeyRevokedError when key has revoked_at set."""
    revoked_key = _make_api_key(revoked_at=_NOW)
    mock_repo.get_by_hash.return_value = revoked_key

    with pytest.raises(ApiKeyRevokedError) as exc_info:
        await service.validate("tlp_revoked_token")

    assert str(_KEY_ID) in str(exc_info.value)


async def test_list_by_user(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    keys = [_make_api_key(), _make_api_key(id=UUID("00000000-0000-0000-0000-000000000003"))]
    mock_repo.list_by_owner.return_value = keys

    result = await service.list_by_user(owner_id=_OWNER_ID)

    assert result == keys
    mock_repo.list_by_owner.assert_called_once_with(_OWNER_ID)


async def test_revoke(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    revoked_key = _make_api_key(revoked_at=_NOW)
    mock_repo.revoke.return_value = revoked_key

    result = await service.revoke(key_id=_KEY_ID, owner_id=_OWNER_ID)

    assert result.is_revoked is True
    mock_repo.revoke.assert_called_once_with(_KEY_ID, _OWNER_ID)


async def test_get_whitelist(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    mock_repo.get_whitelist.return_value = ["rule-001", "rule-002"]

    result = await service.get_whitelist(key_id=_KEY_ID)

    assert result == ["rule-001", "rule-002"]


async def test_add_to_whitelist(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    mock_repo.add_to_whitelist.return_value = None

    await service.add_to_whitelist(key_id=_KEY_ID, rule_id="injection-001")

    mock_repo.add_to_whitelist.assert_called_once_with(_KEY_ID, "injection-001")


async def test_remove_from_whitelist(service: ApiKeyService, mock_repo: AsyncMock) -> None:
    mock_repo.remove_from_whitelist.return_value = None

    await service.remove_from_whitelist(key_id=_KEY_ID, rule_id="injection-001")

    mock_repo.remove_from_whitelist.assert_called_once_with(_KEY_ID, "injection-001")


async def test_hash_token_is_deterministic(service: ApiKeyService) -> None:
    """_hash_token() is deterministic — same input always yields same output."""
    token = "tlp_abc123"  # noqa: S105
    h1 = service._hash_token(token)
    h2 = service._hash_token(token)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex = 64 chars


async def test_is_revoked_property() -> None:
    key = _make_api_key(revoked_at=None)
    assert key.is_revoked is False

    revoked = _make_api_key(revoked_at=_NOW)
    assert revoked.is_revoked is True
