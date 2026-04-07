"""GitHub Releases API client for fetching product releases.

Phase 5 Product Releases Notification feature.
"""

import re
from datetime import datetime
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import httpx
import structlog

from src.domain.models import Release


class GitHubReleasesApiClient:
    """Client for GitHub Releases REST API integration."""

    BASE_URL = "https://api.github.com/repos"

    def __init__(self, owner: str, repo: str, token: str | None = None) -> None:
        """Initialize with GitHub repository owner, repo name, and optional token."""
        # Validate owner and repo names to prevent path traversal
        if not re.match(r"^[a-zA-Z0-9_-]+$", owner):
            raise ValueError(f"Invalid GitHub owner: {owner}")
        if not re.match(r"^[a-zA-Z0-9_.-]+$", repo):
            raise ValueError(f"Invalid GitHub repo: {repo}")

        self.owner = owner
        self.repo = repo
        self.token = token
        self.client = httpx.AsyncClient(timeout=10.0)

    async def fetch_latest_releases(self, per_page: int = 10) -> list[Release]:
        """Fetch latest releases from GitHub, return as Release domain models."""
        url = f"{self.BASE_URL}/{self.owner}/{self.repo}/releases"
        headers = {}

        if self.token:
            headers["Authorization"] = f"token {self.token}"
            headers["Accept"] = "application/vnd.github.v3+json"

        try:
            response = await self.client.get(
                url, headers=headers, params={"per_page": per_page}
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            msg = f"Failed to fetch releases from GitHub: {e}"
            raise RuntimeError(msg) from e
        except httpx.HTTPStatusError as e:
            msg = f"GitHub API error ({e.response.status_code}): {e.response.text}"
            raise RuntimeError(msg) from e

        releases: list[Release] = []
        data = response.json()

        if not isinstance(data, list):
            raise RuntimeError("Unexpected response format from GitHub API")

        for item in data:
            try:
                release = self._parse_github_release(item)
                releases.append(release)
            except (KeyError, ValueError) as e:
                # Skip malformed releases, log and continue
                log = structlog.get_logger()
                log.warning("failed_to_parse_release", error=str(e))
                continue

        return releases

    def _parse_github_release(self, item: dict[str, Any]) -> Release:
        """Parse GitHub release JSON into Release domain model."""
        # GitHub returns ISO 8601 datetime strings
        published_date_str = item.get("published_at") or item.get("created_at")
        if not published_date_str:
            raise ValueError("Missing published_at or created_at")

        # Parse ISO 8601 datetime
        if published_date_str.endswith("Z"):
            published_date_str = published_date_str[:-1] + "+00:00"
        published_date = datetime.fromisoformat(published_date_str)

        # Extract breaking changes from changelog if indicated in body
        # Look for common breaking change patterns: "BREAKING:", "#major", "breaking change", etc.
        changelog_body = item.get("body", "") or ""
        breaking_patterns = [
            r"^#\s*major",  # Semantic versioning comment style
            r"^BREAKING[\s:]",  # Explicit BREAKING marker
            r"^breaking\s+change",  # Standard convention
        ]
        breaking_changes_flag = any(
            re.search(pattern, changelog_body, re.MULTILINE | re.IGNORECASE)
            for pattern in breaking_patterns
        )

        # Deterministic UUID from GitHub release ID (prevents duplicates on resync)
        release_id = uuid5(NAMESPACE_URL, f"github:{item['id']}")

        created_at_str = item.get(
            "created_at", datetime.now(datetime.UTC).isoformat()
        ).replace("Z", "+00:00")
        updated_at_str = item.get(
            "updated_at", datetime.now(datetime.UTC).isoformat()
        ).replace("Z", "+00:00")

        return Release(
            id=release_id,
            title=item.get("name") or item.get("tag_name", "Untitled Release"),
            version=item.get("tag_name", "unknown"),
            published_date=published_date,
            summary=self._extract_summary(changelog_body),
            changelog_html=changelog_body,  # Rendered on frontend with sanitization
            breaking_changes_flag=breaking_changes_flag,
            documentation_url=item.get("html_url"),  # Link to GitHub release
            created_at=datetime.fromisoformat(created_at_str),
            updated_at=datetime.fromisoformat(updated_at_str),
        )

    @staticmethod
    def _extract_summary(changelog: str) -> str:
        """Extract first 200 chars of changelog as summary."""
        if not changelog:
            return ""
        return changelog[:200].strip() + ("..." if len(changelog) > 200 else "")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "GitHubReleasesApiClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
