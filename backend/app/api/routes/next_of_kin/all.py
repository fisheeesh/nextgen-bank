from fastapi import APIRouter, HTTPException, status

from ....core.logging import get_logger
from ....next_of_kin.schema import NextOfKinReadSchema
from ...services.next_of_kin import get_user_next_of_kins
from ..auth.deps import CurrentUser, SessionDep

logger = get_logger()

router = APIRouter(prefix="/next-of-kin")


@router.get(
    "/all",
    response_model=list[NextOfKinReadSchema],
    status_code=status.HTTP_200_OK,
    description="Get all next of kins for the authenticated user",
)
async def list_next_of_kins(
    current_user: CurrentUser,
    session: SessionDep,
) -> list[NextOfKinReadSchema]:
    try:
        next_of_kins = await get_user_next_of_kins(
            user_id=current_user.id,
            session=session,
        )

        # ? baiscally returning list of NextOfKinReadSchemas
        return [NextOfKinReadSchema.model_validate(kin) for kin in next_of_kins]
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(
            f"Failed to retrieve next of kins for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to retrieve next of kin",
                "action": "Please try again later",
            },
        )
