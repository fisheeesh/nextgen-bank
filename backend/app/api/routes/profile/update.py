from fastapi import APIRouter, HTTPException, status

from ....core.logging import get_logger
from ....user_profile.models import Profile
from ....user_profile.schema import ProfileUpdateSchema
from ...services.profile import update_user_profile
from ..auth.deps import CurrentUser, SessionDep

logger = get_logger()

router = APIRouter(prefix="/profile")


@router.patch(
    "/update", response_model=ProfileUpdateSchema, status_code=status.HTTP_200_OK
)
async def update_profile(
    profile_data: ProfileUpdateSchema,
    current_user: CurrentUser,
    session: SessionDep,
) -> Profile:
    try:
        profile = await update_user_profile(
            user_id=current_user.id, profile_data=profile_data, session=session
        )

        logger.info(f"Profile updated for user {current_user.id}")
        return profile
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(
            f"Failed to update a profile for the user {current_user.email}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to update user profile",
                "action": "Please try again later",
            },
        )
