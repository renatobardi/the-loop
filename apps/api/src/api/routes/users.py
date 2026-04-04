"""User profile route handlers — Phase 2 nav/dashboard/profile."""

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

from src.adapters.firebase.auth import FirebaseTokenData, get_firebase_token_data
from src.api.deps import get_user_service
from src.api.middleware import limiter
from src.api.models.users import UserResponse, UserUpdateRequest
from src.domain.exceptions import UserNotFoundError
from src.domain.models import UNSET
from src.domain.services import UserService

router = APIRouter(prefix="/api/v1", tags=["users"])


@router.get(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("60/minute")
async def get_me(
    request: Request,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get or create the authenticated user's profile (upsert on first call).

    Populates display_name from the Firebase token's 'name' claim on creation.
    Subsequent calls return the stored profile unchanged.
    """
    user = await user_service.get_or_create(
        firebase_uid=token_data["firebase_uid"],
        email=token_data["email"],
        display_name=token_data["display_name"],
    )
    return UserResponse.from_domain(user)


@router.patch(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("60/minute")
async def patch_me(
    request: Request,
    body: UserUpdateRequest,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update the authenticated user's profile (partial update).

    Omitting a field leaves it unchanged. Sending null for display_name returns 422.
    """
    job_title = body.job_title if "job_title" in body.model_fields_set else UNSET
    try:
        user = await user_service.update_profile(
            user_id=token_data["user_id"],
            display_name=body.display_name,
            job_title=job_title,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from e
    return UserResponse.from_domain(user)
