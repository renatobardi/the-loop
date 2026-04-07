"""Typed domain exceptions for the Incident module."""

__all__ = [
    "ActionItemNotFoundError",
    "ApiKeyInvalidError",
    "ApiKeyNotFoundError",
    "ApiKeyRevokedError",
    "AttachmentNotFoundError",
    "DuplicateResponderError",
    "DuplicateSourceUrlError",
    "IncidentHasActiveRuleError",
    "IncidentMissingPostmortumError",
    "IncidentNotFoundError",
    "InvalidVersionFormatError",
    "OptimisticLockError",
    "PostmortumAlreadyExistsError",
    "PostmortumLockedError",
    "PostmortumNotFoundError",
    "ReleaseAlreadyExistsError",
    "ReleaseNotFoundError",
    "ResponderNotFoundError",
    "RuleVersionNotFoundError",
    "ScanNotFoundError",
    "TimelineEventNotFoundError",
    "UserNotFoundError",
    "VersionAlreadyExistsError",
]


class IncidentNotFoundError(Exception):
    def __init__(self, incident_id: str) -> None:
        self.incident_id = incident_id
        super().__init__(f"Incident not found: {incident_id}")


class DuplicateSourceUrlError(Exception):
    def __init__(self, source_url: str) -> None:
        self.source_url = source_url
        super().__init__(f"source_url already exists: {source_url}")


class OptimisticLockError(Exception):
    def __init__(self, incident_id: str, current_version: int) -> None:
        self.incident_id = incident_id
        self.current_version = current_version
        super().__init__(
            f"Incident {incident_id} was modified by another process "
            f"(current version: {current_version})"
        )


class IncidentHasActiveRuleError(Exception):
    def __init__(self, incident_id: str, semgrep_rule_id: str) -> None:
        self.incident_id = incident_id
        self.semgrep_rule_id = semgrep_rule_id
        super().__init__(
            f"Cannot modify incident {incident_id}: active Semgrep rule {semgrep_rule_id}"
        )


class IncidentMissingPostmortumError(Exception):
    def __init__(self, incident_id: str) -> None:
        self.incident_id = incident_id
        super().__init__(
            f"Cannot resolve incident {incident_id}: postmortem is required before closure. "
            f"Create a postmortem at POST /api/v1/incidents/{incident_id}/postmortem"
        )


class TimelineEventNotFoundError(Exception):
    def __init__(self, event_id: str) -> None:
        self.event_id = event_id
        super().__init__(f"Timeline event not found: {event_id}")


class DuplicateResponderError(Exception):
    def __init__(self, incident_id: str, user_id: str) -> None:
        self.incident_id = incident_id
        self.user_id = user_id
        super().__init__(f"User {user_id} is already a responder for incident {incident_id}")


class ResponderNotFoundError(Exception):
    def __init__(self, responder_id: str) -> None:
        self.responder_id = responder_id
        super().__init__(f"Responder not found: {responder_id}")


class ActionItemNotFoundError(Exception):
    def __init__(self, item_id: str) -> None:
        self.item_id = item_id
        super().__init__(f"Action item not found: {item_id}")


class AttachmentNotFoundError(Exception):
    def __init__(self, attachment_id: str) -> None:
        self.attachment_id = attachment_id
        super().__init__(f"Attachment not found: {attachment_id}")


# ─── Phase B: API Integration & Versioning ───────────────────────────────────


class RuleVersionNotFoundError(Exception):
    def __init__(self, version: str) -> None:
        self.version = version
        super().__init__(f"Rule version not found: {version}")


class VersionAlreadyExistsError(Exception):
    def __init__(self, version: str) -> None:
        self.version = version
        super().__init__(f"Rule version already exists: {version}")


class InvalidVersionFormatError(Exception):
    def __init__(self, version: str) -> None:
        self.version = version
        super().__init__(f"Invalid semantic version format: {version}. Expected: X.Y.Z")


# ─── Phase C: Incident Knowledge Capture (Postmortem) ────────────────────────


class PostmortumNotFoundError(Exception):
    def __init__(self, postmortem_id: str | object) -> None:
        self.postmortem_id = postmortem_id
        super().__init__(f"Postmortem not found: {postmortem_id}")


class PostmortumAlreadyExistsError(Exception):
    def __init__(self, incident_id: str | object) -> None:
        self.incident_id = incident_id
        super().__init__(
            f"Postmortem already exists for incident {incident_id}. "
            f"Use PUT to update existing postmortem."
        )


class PostmortumLockedError(Exception):
    def __init__(self, postmortem_id: str | object) -> None:
        self.postmortem_id = postmortem_id
        super().__init__(
            f"Postmortem {postmortem_id} is locked after incident resolution. "
            f"Create a new incident if you need to add analysis."
        )


# ─── Phase 2: Navigation, Dashboard & User Profile ───────────────────────────


class UserNotFoundError(Exception):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")


# ─── Phase 4: Semgrep Platform — API Keys & Scans ────────────────────────────


class ApiKeyNotFoundError(Exception):
    def __init__(self, key_id: str) -> None:
        self.key_id = key_id
        super().__init__(f"API key not found: {key_id}")


class ApiKeyRevokedError(Exception):
    def __init__(self, key_id: str) -> None:
        self.key_id = key_id
        super().__init__(f"API key has been revoked: {key_id}")


class ApiKeyInvalidError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid API key")


class ScanNotFoundError(Exception):
    def __init__(self, scan_id: str) -> None:
        self.scan_id = scan_id
        super().__init__(f"Scan not found: {scan_id}")


# ─── Phase 5: Product Releases Notification ───────────────────────────────


class ReleaseNotFoundError(Exception):
    def __init__(self, release_id: str) -> None:
        self.release_id = release_id
        super().__init__(f"Release not found: {release_id}")


class ReleaseAlreadyExistsError(Exception):
    def __init__(self, version: str) -> None:
        self.version = version
        super().__init__(f"Release with version {version} already exists")
