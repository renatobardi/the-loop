"""API routes for scan registration and reporting — Phase 4 Semgrep platform."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.adapters.firebase.auth import FirebaseTokenData, get_firebase_token_data
from src.api.deps import ApiKeyContext, get_optional_identity, get_scan_service
from src.api.middleware import limiter
from src.domain.models import Scan
from src.domain.services import ScanService

router = APIRouter(prefix="/api/v1", tags=["scans"])


# ─── Request / Response models ───────────────────────────────────────────────


class FindingInput(BaseModel):
    rule_id: str
    file_path: str
    line_number: int
    severity: str


class RegisterScanRequest(BaseModel):
    repository: str
    branch: str
    pr_number: int | None = None
    rules_version: str
    findings_count: int
    errors_count: int
    warnings_count: int
    duration_ms: int
    findings: list[FindingInput] = []


class ScanResponse(BaseModel):
    id: UUID
    api_key_id: UUID
    repository: str
    branch: str
    pr_number: int | None
    rules_version: str
    findings_count: int
    errors_count: int
    warnings_count: int
    duration_ms: int
    created_at: datetime

    @classmethod
    def from_domain(cls, scan: Scan) -> "ScanResponse":
        return cls(
            id=scan.id,
            api_key_id=scan.api_key_id,
            repository=scan.repository,
            branch=scan.branch,
            pr_number=scan.pr_number,
            rules_version=scan.rules_version,
            findings_count=scan.findings_count,
            errors_count=scan.errors_count,
            warnings_count=scan.warnings_count,
            duration_ms=scan.duration_ms,
            created_at=scan.created_at,
        )


class ScanListResponse(BaseModel):
    items: list[ScanResponse]
    total: int


# ─── Routes ──────────────────────────────────────────────────────────────────


@router.post(
    "/scans",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("60/minute")
async def register_scan(
    request: Request,
    payload: RegisterScanRequest,
    identity: object = Depends(get_optional_identity),
    service: ScanService = Depends(get_scan_service),
) -> ScanResponse:
    """Register a Semgrep scan result (API key auth required — Bearer tlp_...).

    Continue-on-error: returns 200/201 even if edge errors occur.
    """
    if not isinstance(identity, ApiKeyContext):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key authentication required (Bearer tlp_...)",
        )

    findings_dicts: list[dict[str, str | int]] = [
        {
            "rule_id": f.rule_id,
            "file_path": f.file_path,
            "line_number": f.line_number,
            "severity": f.severity,
        }
        for f in payload.findings
    ]

    scan = await service.register(
        api_key=identity.api_key,
        repository=payload.repository,
        branch=payload.branch,
        pr_number=payload.pr_number,
        rules_version=payload.rules_version,
        findings_count=payload.findings_count,
        errors_count=payload.errors_count,
        warnings_count=payload.warnings_count,
        duration_ms=payload.duration_ms,
        findings=findings_dicts,
    )
    return ScanResponse.from_domain(scan)


@router.get(
    "/scans",
    response_model=ScanListResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("60/minute")
async def list_scans(
    request: Request,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    service: ScanService = Depends(get_scan_service),
) -> ScanListResponse:
    """List recent scans for the authenticated user (all their API keys)."""
    owner_id = token_data["user_id"]
    scans = await service.list_by_user(owner_id=owner_id)
    items = [ScanResponse.from_domain(s) for s in scans]
    return ScanListResponse(items=items, total=len(items))


@router.get(
    "/scans/summary",
    status_code=status.HTTP_200_OK,
)
@limiter.limit("60/minute")
async def get_scan_summary(
    request: Request,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    service: ScanService = Depends(get_scan_service),
) -> dict[str, object]:
    """Return scan summary (totals, scans by week, top rules) for the authenticated user."""
    owner_id = token_data["user_id"]
    return await service.get_summary(owner_id=owner_id)
