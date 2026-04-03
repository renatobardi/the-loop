"""In-memory cache adapter for rule versions — Phase B API integration."""

from datetime import UTC, datetime, timedelta

from src.domain.models import RuleVersion

# Cache key constant
RULES_LATEST_CACHE_KEY = "rules:latest"


class RuleVersionCache:
    """In-memory cache with TTL for rule versions (Phase B)."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        """Initialize cache with TTL.

        Args:
            ttl_seconds: Time-to-live for cached entries (default: 300s = 5 minutes)
        """
        self.cache: dict[str, tuple[RuleVersion, datetime]] = {}
        self.ttl_seconds = ttl_seconds

    async def get_latest(self) -> RuleVersion | None:
        """Get cached latest rule version if not expired.

        Returns:
            RuleVersion if cached and not expired, None otherwise.
        """
        key = RULES_LATEST_CACHE_KEY
        if key not in self.cache:
            return None

        cached_version, expires_at = self.cache[key]
        now = datetime.now(UTC)

        if now < expires_at:
            return cached_version

        # Expired, remove and return None
        del self.cache[key]
        return None

    async def set_latest(self, rule_version: RuleVersion) -> None:
        """Cache the latest rule version.

        Args:
            rule_version: RuleVersion object to cache
        """
        key = RULES_LATEST_CACHE_KEY
        expires_at = datetime.now(UTC) + timedelta(seconds=self.ttl_seconds)
        self.cache[key] = (rule_version, expires_at)

    async def invalidate(self) -> None:
        """Invalidate the latest rule version cache.

        Called after publishing a new version to ensure next request gets fresh data.
        """
        key = RULES_LATEST_CACHE_KEY
        self.cache.pop(key, None)

    async def clear_all(self) -> None:
        """Clear all cached entries (for testing or maintenance)."""
        self.cache.clear()

    def get_cache_stats(self) -> dict[str, int | list[dict[str, str | int]]]:
        """Get cache statistics for monitoring.

        Returns:
            Dict with cache size, TTL, and entry details.
        """
        now = datetime.now(UTC)
        entries: list[dict[str, str | int]] = []
        for key, (_, expires_at) in self.cache.items():
            remaining_ttl = (expires_at - now).total_seconds()
            entries.append(
                {
                    "key": key,
                    "remaining_ttl_seconds": max(0, int(remaining_ttl)),
                }
            )

        return {
            "total_entries": len(self.cache),
            "ttl_seconds": self.ttl_seconds,
            "entries": entries,
        }
