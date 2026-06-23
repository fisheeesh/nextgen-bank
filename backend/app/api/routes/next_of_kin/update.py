from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from ....core.logging import get_logger
from ....next_of_kin.schema import NextOfKinReadSchema, NextOfKinUpdateSchema
from ...services.next_of_kin import update_next_of_kin
from ..auth.deps import CurrentUser, SessionDep

logger = get_logger()

router = APIRouter(prefix="/next-of-kin")


@router.patch(
    "/{next_of_kin_id}",
    response_model=NextOfKinReadSchema,
    status_code=status.HTTP_200_OK,
    description="Update a next of kin. Onlly provided fields will be updated",
)
async def update_next_of_kin_route(
    next_of_kin_id: UUID,
    update_data: NextOfKinUpdateSchema,
    current_user: CurrentUser,
    session: SessionDep,
) -> NextOfKinReadSchema:
    try:
        next_of_kin = await update_next_of_kin(
            user_id=current_user.id,
            next_of_kin_id=next_of_kin_id,
            update_data=update_data,
            session=session,
        )
        logger.info(f"User {current_user.email} update next of kin: {next_of_kin_id}")
        return NextOfKinReadSchema.model_validate(next_of_kin)
    except HTTPException as http_ex:
        logger.warning(
            f"Next of kin update failed for user {current_user.email}: {http_ex.detail}"
        )
        raise http_ex
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to update next of kin",
                "action": "Please try again later",
            },
        )
