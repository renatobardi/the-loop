"""Typed domain exceptions for the Incident module."""


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
