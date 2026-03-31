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
            f"Cannot modify incident {incident_id}: "
            f"active Semgrep rule {semgrep_rule_id}"
        )
