from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from sqlmodel import select

from ....core.logging import get_logger
from ....transactions.models import IdempotencyKey
from ....virtual_card.schema import CardTopUpResponseSchema, CardTopUpSchema
from ...services.card import top_up_virtual_card
from ..auth.deps import CurrentUser, SessionDep

logger = get_logger()

router = APIRouter(prefix="/virtual-card")


def validate_uuid4(value: str) -> str:
    try:
        uuid_obj = UUID(value, version=4)
        if str(uuid_obj) != value.lower():
            raise ValueError("Not a valid UUID")
        return value
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Idempotnecy-Key must be a valid UUID version 4",
            },
        )


@router.post(
    "/{card_id}/top-id",
    response_model=CardTopUpResponseSchema,
    status_code=status.HTTP_200_OK,
    description="Top up a virtual card form a bank account. Card must be active",
)
async def top_up_card(
    card_id: UUID,
    top_up_data: CardTopUpSchema,
    current_user: CurrentUser,
    session: SessionDep,
    idempotency_key: str = Header(description="Idempotency key for the top-up request"),
) -> CardTopUpResponseSchema:
    try:
        idempotency_key = validate_uuid4(idempotency_key)
        if not idempotency_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Idempotency-Key header is required",
                },
            )

        existing_key_result = await session.exec(
            select(IdempotencyKey).where(
                IdempotencyKey.key == idempotency_key,
                IdempotencyKey.user_id == current_user.id,
                IdempotencyKey.endpoint == "/virtual-card/top-up",
                IdempotencyKey.expires_at > datetime.now(timezone.utc),
            )
        )

        existing_key = existing_key_result.first()

        if existing_key:
            return CardTopUpResponseSchema(
                status="success",
                message="Retrieved from cache",
                data=existing_key.response_body,
            )

        card, transaction = await top_up_virtual_card(
            card_id=card_id,
            account_number=top_up_data.account_number,
            amount=top_up_data.amount,
            description=top_up_data.description,
            session=session,
        )

        response = CardTopUpResponseSchema(
            status="success",
            message="Card topped up successfully",
            data={
                "card_id": str(card.id),
                "transaction_id": str(transaction.id),
                "amount": str(transaction.amount),
                "new_balance": str(card.available_balance),
                "reference": transaction.reference,
            },
        )

        idempotency_record = IdempotencyKey(
            key=idempotency_key,
            user_id=current_user.id,
            endpoint="/virtual-card/top-up",
            response_code=status.HTTP_200_OK,
            response_body=response.model_dump(),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )

        session.add(idempotency_record)
        await session.commit()

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to top-up card: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to top-up card",
            },
        )
