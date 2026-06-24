from ....auth.schema import RoleChoicesSchema
from fastapi import APIRouter, HTTPException, status

from ....transactions.schema import DepositRequestSchema
from ....transactions.enums import TransactionTypeEnum
from ....core.logging import get_logger
from ....core.services.deposit_alert import send_deposit_alert
from ...services.transaction import process_deposit
from ..auth.deps import CurrentUser, SessionDep

logger = get_logger()

router = APIRouter(prefix="/bank-account")


@router.post("/deposit", status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit_data: DepositRequestSchema,
    current_user: CurrentUser,
    session: SessionDep,
):
    if current_user.role != RoleChoicesSchema.TELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": "error",
                "message": "Only teller can process deposits",
            },
        )

    try:
        transaction, account, account_owner = await process_deposit(
            amount=deposit_data.amount,
            account_id=deposit_data.account_id,
            teller_id=current_user.id,
            description=deposit_data.description,
            session=session,
        )

        if not account.account_number:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"status": "error", "message": "Account number is required"},
            )

        try:
            currency_value = account.currency.value
            await send_deposit_alert(
                email=account_owner.email,
                full_name=account_owner.full_name,
                action=TransactionTypeEnum.Deposit.value,
                amount=transaction.amount,
                account_name=account.account_name,
                account_number=account.account_number,
                currency=currency_value,
                description=transaction.description,
                transaction_date=transaction.completed_at or transaction.create_at,
                reference=transaction.reference,
                balance=transaction.balance_after,
            )
        except Exception as email_error:
            logger.error(f"Failed to send transaction alert: {email_error}")

        return {
            "status": "success",
            "message": "Deposit processed successfully",
            "data": {
                "transaction_id": transaction.id,
                "reference": transaction.reference,
                "amount": transaction.amount,
                "balance": transaction.balance_after,
                "status": transaction.status,
            },
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Failed ot process deposit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to process deposit",
            },
        )
