from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ....auth.schema import RoleChoicesSchema
from ....core.logging import get_logger
from ....transactions.schema import (
    PaginatedHistoryResponseSchema,
    RiskHistoryItemSchema,
    RiskHistoryParams,
)
from ...services.transaction import get_user_risk_history
from ..auth.deps import CurrentUser, SessionDep

logger = get_logger()

router = APIRouter(prefix="/transaction")


def get_risk_history_params(
    start_date: datetime | None = Query(
        default=None, description="Filter from this date"
    ),
    end_date: datetime | None = Query(
        default=None, description="Filter until this date"
    ),
    min_risk_score: float | None = Query(
        default=None, ge=0, le=1, description="Minimum risk score"
    ),
    user_id: str | None = Query(
        default=None,
        description="Filter by specific user ID (only for account executives)",
    ),
    skip: int = Query(
        default=0, ge=0, description="Number of records to skip (for pagination)"
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return (for pagination)",
    ),
) -> RiskHistoryParams:
    return RiskHistoryParams(
        start_date=start_date,
        end_date=end_date,
        min_risk_score=min_risk_score,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/risk-history",
    response_model=PaginatedHistoryResponseSchema,
    description="Get paginated risk analysis history for transactions. Only accessible to account executives",
)
async def get_risk_history(
    current_user: CurrentUser,
    session: SessionDep,
    params: RiskHistoryParams = Depends(get_risk_history_params),
) -> PaginatedHistoryResponseSchema:
    try:
        if current_user.role != RoleChoicesSchema.ACCOUNT_EXECUTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "status": "error",
                    "message": "Only account executives can review transactions",
                },
            )

        target_user_id = None

        if params.user_id:
            try:
                target_user_id = UUID(params.user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"status": "error", "message": "Invalid user ID format"},
                )
        else:
            target_user_id = current_user.id

        history_dicts, total_count = await get_user_risk_history(
            user_id=target_user_id,
            start_date=params.start_date,
            end_date=params.end_date,
            min_risk_score=params.min_risk_score,
            skip=params.skip,
            limit=params.limit,
            session=session,
        )

        history_items = [
            RiskHistoryItemSchema.model_validate(item) for item in history_dicts
        ]

        return PaginatedHistoryResponseSchema(
            total=total_count,
            skip=params.skip,
            limit=params.limit,
            items=history_items,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get risk history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to retrieve risk history",
                "action": "Please try again later",
            },
        )
