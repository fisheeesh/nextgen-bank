from fastapi import APIRouter, HTTPException, status

from ....bank_account.schema import BankAccountCreateSchema, BankAccountReadSchema
from ....core.logging import get_logger
from ....core.services.bank_account_created_email import send_account_created_email
from ...services.bank_account import create_bank_account
from ..auth.deps import CurrentUser, SessionDep

logger = get_logger()

router = APIRouter(prefix="/bank-account")


@router.post(
    "/create",
    response_model=BankAccountReadSchema,
    status_code=status.HTTP_201_CREATED,
    description="Create a new bank account. Require completed profile and at least one next of kin. Maximum 3 accounts per user",
)
async def create_account(
    account_data: BankAccountCreateSchema,
    current_user: CurrentUser,
    session: SessionDep,
) -> BankAccountReadSchema:
    try:
        account = await create_bank_account(
            user_id=current_user.id, account_data=account_data, session=session
        )

        try:
            if not account.account_number:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "status": "error",
                        "message": "Account number not generate",
                    },
                )

            await send_account_created_email(
                email=current_user.email,
                full_name=current_user.full_name,
                account_number=account.account_number,
                account_name=account.account_name,
                account_type=account.account_type.value,
                currency=account.currency.value,
                identification_type=current_user.profile.means_of_identification.value,
            )
        except Exception as e:
            logger.error(f"Failed to send account creation email: {e}")

        logger.info(f"Created account for user {current_user.email}")
        return BankAccountReadSchema.model_validate(account)
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to create account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to create account",
                "action": "Please try again later",
            },
        )
