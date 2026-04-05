"""In-memory analytics cache with 5-minute TTL.

Keyed on sorted parameter tuples to ensure cache consistency regardless
of argument ordering. Thread-safe for single-process asyncio usage.
"""

import time
from typing import Any

_TTL_SECONDS = 300  # 5 minutes


class AnalyticsCache:
    """Simple in-memory cache with TTL expiry for analytics query results."""

    def __init__(self, ttl_seconds: int = _TTL_SECONDS) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[Any, float]] = {}

    @staticmethod
    def make_key(method: str, params: dict[str, Any]) -> str:
        """Build a stable cache key by sorting params alphabetically.

        List values are sorted before stringification to ensure stable keys
        regardless of order (e.g., teams=['a','b'] and teams=['b','a'] produce
        the same key).
        """
        sorted_items = sorted(
            (
                (k, str(sorted(v) if isinstance(v, list) else v))
                for k, v in params.items()
            ),
            key=lambda x: x[0],
        )
        parts = "&".join(f"{k}={v}" for k, v in sorted_items)
        return f"{method}?{parts}"

    def get(self, key: str) -> Any | None:
        """Return cached value if present and not expired, else None."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        """Store value with TTL expiry."""
        self._store[key] = (value, time.monotonic() + self._ttl)

    def invalidate_all(self) -> None:
        """Clear all cached entries. Called to invalidate cache when analytics data changes."""
        self._store.clear()

    def size(self) -> int:
        """Return number of currently stored (possibly expired) entries."""
        return len(self._store)
