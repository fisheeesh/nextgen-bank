from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from ....core.logging import get_logger
from ...services.next_of_kin import delete_next_of_kin
from ..auth.deps import CurrentUser, SessionDep

logger = get_logger()

router = APIRouter(prefix="/next-of-kin")


@router.delete(
    "/{next_of_kin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a next of kin. Cannot delete if it's the only one remaining",
)
async def delete_next_of_kin_route(
    next_of_kin_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    try:
        await delete_next_of_kin(
            user_id=current_user.id, next_of_kin_id=next_of_kin_id, session=session
        )
    except HTTPException as http_ex:
        logger.warning(
            f"Next of kin deletion failed for user {current_user.email}: {http_ex}"
        )
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to delete next of kin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Faild to delete next of kin",
                "action": "Please try again later",
            },
        )
