"""Unit tests for AnalyticsCache — TTL expiry and key generation."""

import time
from unittest.mock import patch

import pytest

from src.adapters.postgres.analytics_cache import AnalyticsCache


class TestMakeKey:
    def test_basic_key(self) -> None:
        key = AnalyticsCache.make_key("get_summary", {"period": "month", "status": "all"})
        assert "get_summary?" in key
        assert "period=month" in key
        assert "status=all" in key

    def test_params_sorted_alphabetically(self) -> None:
        k1 = AnalyticsCache.make_key("m", {"z": "1", "a": "2"})
        k2 = AnalyticsCache.make_key("m", {"a": "2", "z": "1"})
        assert k1 == k2

    def test_list_values_sorted(self) -> None:
        k1 = AnalyticsCache.make_key("m", {"teams": ["b", "a"]})
        k2 = AnalyticsCache.make_key("m", {"teams": ["a", "b"]})
        assert k1 == k2

    def test_different_methods_produce_different_keys(self) -> None:
        k1 = AnalyticsCache.make_key("get_summary", {"period": "month"})
        k2 = AnalyticsCache.make_key("get_timeline", {"period": "month"})
        assert k1 != k2

    def test_different_params_produce_different_keys(self) -> None:
        k1 = AnalyticsCache.make_key("m", {"period": "month"})
        k2 = AnalyticsCache.make_key("m", {"period": "week"})
        assert k1 != k2


class TestCacheGetSet:
    def test_returns_none_for_missing_key(self) -> None:
        cache = AnalyticsCache()
        assert cache.get("nonexistent") is None

    def test_returns_value_immediately_after_set(self) -> None:
        cache = AnalyticsCache()
        cache.set("k", {"total": 42})
        assert cache.get("k") == {"total": 42}

    def test_stores_any_value_type(self) -> None:
        cache = AnalyticsCache()
        cache.set("list", [1, 2, 3])
        cache.set("none", None)
        cache.set("int", 0)
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("none") is None  # None is a valid cached value
        assert cache.get("int") == 0

    def test_overwrite_existing_key(self) -> None:
        cache = AnalyticsCache()
        cache.set("k", "first")
        cache.set("k", "second")
        assert cache.get("k") == "second"


class TestCacheTTL:
    def test_entry_available_before_ttl(self) -> None:
        cache = AnalyticsCache(ttl_seconds=300)
        now = time.monotonic()
        cache.set("k", "value")
        with patch("time.monotonic", return_value=now + 299):
            assert cache.get("k") == "value"

    def test_entry_expired_after_ttl(self) -> None:
        cache = AnalyticsCache(ttl_seconds=300)
        now = time.monotonic()
        cache.set("k", "value")
        with patch("time.monotonic", return_value=now + 301):
            assert cache.get("k") is None

    def test_expired_entry_removed_from_store(self) -> None:
        cache = AnalyticsCache(ttl_seconds=300)
        now = time.monotonic()
        cache.set("k", "value")
        assert cache.size() == 1
        with patch("time.monotonic", return_value=now + 301):
            cache.get("k")
        assert cache.size() == 0

    def test_custom_ttl_respected(self) -> None:
        cache = AnalyticsCache(ttl_seconds=60)
        now = time.monotonic()
        cache.set("k", "value")
        with patch("time.monotonic", return_value=now + 59):
            assert cache.get("k") == "value"
        with patch("time.monotonic", return_value=now + 61):
            assert cache.get("k") is None

    def test_boundary_at_exact_ttl_is_expired(self) -> None:
        # expires_at = now + ttl; get checks monotonic() > expires_at
        # so at exactly expires_at it is NOT yet expired (strictly greater)
        cache = AnalyticsCache(ttl_seconds=300)
        now = time.monotonic()
        cache.set("k", "value")
        with patch("time.monotonic", return_value=now + 300):
            # monotonic() == expires_at → NOT > expires_at → still valid
            assert cache.get("k") == "value"
        with patch("time.monotonic", return_value=now + 300.001):
            assert cache.get("k") is None


class TestInvalidateAll:
    def test_clears_all_entries(self) -> None:
        cache = AnalyticsCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.size() == 3
        cache.invalidate_all()
        assert cache.size() == 0
        assert cache.get("a") is None

    def test_invalidate_empty_cache_is_safe(self) -> None:
        cache = AnalyticsCache()
        cache.invalidate_all()  # should not raise
        assert cache.size() == 0
