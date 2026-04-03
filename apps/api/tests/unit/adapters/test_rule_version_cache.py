"""Unit tests for RuleVersionCache."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.adapters.postgres.cache import RuleVersionCache
from src.domain.models import Rule, RuleVersion, RuleVersionStatus


@pytest.fixture
def cache() -> RuleVersionCache:
    """Create a RuleVersionCache with 1-second TTL for testing."""
    return RuleVersionCache(ttl_seconds=1)


@pytest.fixture
def sample_rule_version() -> RuleVersion:
    """Create a sample RuleVersion for caching."""
    return RuleVersion(
        id=uuid4(),
        version="0.1.0",
        rules=[
            Rule(
                id="injection-001",
                languages=["python"],
                message="SQL injection",
                severity="ERROR",
                metadata={},
                patterns=[],
            )
        ],
        status=RuleVersionStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
        published_by=uuid4(),
    )


@pytest.mark.asyncio
class TestRuleVersionCache:
    """Test RuleVersionCache methods."""

    async def test_cache_miss_empty(self, cache: RuleVersionCache) -> None:
        """Test get_latest returns None when cache is empty."""
        result = await cache.get_latest()
        assert result is None

    async def test_cache_set_and_get(
        self, cache: RuleVersionCache, sample_rule_version: RuleVersion
    ) -> None:
        """Test set_latest and get_latest work together."""
        await cache.set_latest(sample_rule_version)
        result = await cache.get_latest()

        assert result == sample_rule_version
        assert result.version == "0.1.0"

    async def test_cache_hit_counter(
        self, cache: RuleVersionCache, sample_rule_version: RuleVersion
    ) -> None:
        """Test that cache hits return same object."""
        await cache.set_latest(sample_rule_version)

        hit1 = await cache.get_latest()
        hit2 = await cache.get_latest()

        assert hit1 == hit2
        assert hit1.id == sample_rule_version.id

    async def test_cache_invalidate(
        self, cache: RuleVersionCache, sample_rule_version: RuleVersion
    ) -> None:
        """Test invalidate removes cached entry."""
        await cache.set_latest(sample_rule_version)
        assert await cache.get_latest() is not None

        await cache.invalidate()
        assert await cache.get_latest() is None

    async def test_cache_ttl_expiration(
        self, sample_rule_version: RuleVersion
    ) -> None:
        """Test cache entries expire after TTL."""
        import asyncio

        # Create cache with 0.1 second TTL
        cache = RuleVersionCache(ttl_seconds=0)
        await cache.set_latest(sample_rule_version)

        # Should be cached immediately
        assert await cache.get_latest() is not None

        # Wait for expiration
        await asyncio.sleep(0.2)

        # Should be expired
        assert await cache.get_latest() is None

    async def test_cache_stats(
        self, cache: RuleVersionCache, sample_rule_version: RuleVersion
    ) -> None:
        """Test get_cache_stats returns correct information."""
        await cache.set_latest(sample_rule_version)
        stats = cache.get_cache_stats()

        assert stats["total_entries"] == 1
        assert stats["ttl_seconds"] == 1
        assert len(stats["entries"]) == 1
        assert stats["entries"][0]["key"] == "rules:latest"
        assert stats["entries"][0]["remaining_ttl_seconds"] <= 1

    async def test_cache_clear_all(
        self, cache: RuleVersionCache, sample_rule_version: RuleVersion
    ) -> None:
        """Test clear_all removes all entries."""
        await cache.set_latest(sample_rule_version)
        assert await cache.get_latest() is not None

        await cache.clear_all()
        assert await cache.get_latest() is None

    async def test_cache_multiple_invalidations(
        self, cache: RuleVersionCache, sample_rule_version: RuleVersion
    ) -> None:
        """Test multiple invalidations are idempotent."""
        await cache.set_latest(sample_rule_version)
        await cache.invalidate()
        await cache.invalidate()  # Should not raise
        assert await cache.get_latest() is None
