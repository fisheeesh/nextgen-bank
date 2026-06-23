from fastapi import APIRouter, HTTPException, status

from ....core.logging import get_logger
from ....next_of_kin.schema import NextOfKinCreateSchema, NextOfKinReadSchema
from ...services.next_of_kin import create_next_of_kin
from ..auth.deps import SessionDep, CurrentUser

logger = get_logger()

router = APIRouter(prefix="/next-of-kin")


@router.post(
    "/create",
    response_model=NextOfKinCreateSchema,
    status_code=status.HTTP_201_CREATED,
    description="Create a new next of kin. Maximum 3 per user, only one can be primary",
)
async def create_next_of_kin_route(
    next_of_kin_data: NextOfKinCreateSchema,
    current_user: CurrentUser,
    session: SessionDep,
) -> NextOfKinReadSchema:
    try:
        next_of_kin = await create_next_of_kin(
            user_id=current_user.id,
            next_of_kin_data=next_of_kin_data,
            session=session,
        )
        logger.info(
            f"User {current_user.email} created an new next of kin: {next_of_kin.full_name}"
        )
        return next_of_kin
    except HTTPException as http_ex:
        logger.warning(
            f"Next of kin creation failed for user {current_user.email}: {http_ex.detail}"
        )
        raise http_ex
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to create next of kin",
            },
        )
