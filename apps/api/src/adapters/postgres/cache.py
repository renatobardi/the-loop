"""In-memory cache adapter for rule versions — Phase B API integration."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from domain.models import RuleVersion


class RuleVersionCache:
    """In-memory cache with TTL for rule versions (Phase B)."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        """Initialize cache with TTL.

        Args:
            ttl_seconds: Time-to-live for cached entries (default: 300s = 5 minutes)
        """
        self.cache: dict[str, tuple[RuleVersion, datetime]] = {}
        self.ttl_seconds = ttl_seconds

    async def get_latest(self) -> Optional[RuleVersion]:
        """Get cached latest rule version if not expired.

        Returns:
            RuleVersion if cached and not expired, None otherwise.
        """
        key = "rules:latest"
        if key not in self.cache:
            return None

        cached_version, expires_at = self.cache[key]
        now = datetime.now(timezone.utc)

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
        key = "rules:latest"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds)
        self.cache[key] = (rule_version, expires_at)

    async def invalidate(self) -> None:
        """Invalidate the latest rule version cache.

        Called after publishing a new version to ensure next request gets fresh data.
        """
        key = "rules:latest"
        self.cache.pop(key, None)

    async def clear_all(self) -> None:
        """Clear all cached entries (for testing or maintenance)."""
        self.cache.clear()

    def get_cache_stats(self) -> dict:
        """Get cache statistics for monitoring.

        Returns:
            Dict with cache size and TTL info.
        """
        now = datetime.now(timezone.utc)
        entries = []
        for key, (_, expires_at) in self.cache.items():
            remaining_ttl = (expires_at - now).total_seconds()
            entries.append({"key": key, "remaining_ttl_seconds": max(0, remaining_ttl)})

        return {"total_entries": len(self.cache), "ttl_seconds": self.ttl_seconds, "entries": entries}
