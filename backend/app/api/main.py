from fastapi import APIRouter

from .routes import home
from .routes.auth import activate, login, logout, password_reset, refresh, register
from .routes.bank_account import activate as activate_bank_account
from .routes.bank_account import create as create_bank_account
from .routes.bank_account import (
    deposit,
    statement,
    transaction_history,
    transfer,
    withdrawal,
)
from .routes.card import (
    activate as activate_card,
)
from .routes.card import (
    block,
    topup,
)
from .routes.card import (
    create as create_card,
)
from .routes.card import (
    delete as delete_card,
)
from .routes.next_of_kin import all
from .routes.next_of_kin import (
    create as create_next_of_kin,
)
from .routes.next_of_kin import delete as delete_next_of_kin
from .routes.next_of_kin import (
    update as update_next_of_kin,
)
from .routes.profile import all_profiles, create, me, update, upload
from .routes.transaction import fraud_review, risk_history
from .routes.ml import api

api_router = APIRouter()

api_router.include_router(home.router)

# ? Auth routes
api_router.include_router(register.router, tags=["Auth"])
api_router.include_router(activate.router, tags=["Auth"])
api_router.include_router(login.router, tags=["Auth"])
api_router.include_router(password_reset.router, tags=["Auth"])
api_router.include_router(refresh.router, tags=["Auth"])
api_router.include_router(logout.router, tags=["Auth"])

# ? Profile routes
api_router.include_router(create.router, tags=["Profile"])
api_router.include_router(update.router, tags=["Profile"])
api_router.include_router(upload.router, tags=["Profile"])
api_router.include_router(me.router, tags=["Profile"])
api_router.include_router(all_profiles.router, tags=["Profile"])

# ? Next of Kin routes
api_router.include_router(create_next_of_kin.router, tags=["Next Of Kin"])
api_router.include_router(all.router, tags=["Next Of Kin"])
api_router.include_router(update_next_of_kin.router, tags=["Next Of Kin"])
api_router.include_router(delete_next_of_kin.router, tags=["Next Of Kin"])

# ? Bank Account routes
api_router.include_router(create_bank_account.router, tags=["Bank Account"])
api_router.include_router(activate_bank_account.router, tags=["Bank Account"])
api_router.include_router(deposit.router, tags=["Bank Account"])
api_router.include_router(transfer.router, tags=["Bank Account"])
api_router.include_router(withdrawal.router, tags=["Bank Account"])
api_router.include_router(transaction_history.router, tags=["Bank Account"])
api_router.include_router(statement.router, tags=["Bank Account"])

# ? Virtual Card
api_router.include_router(create_card.router, tags=["Virtual Card"])
api_router.include_router(activate_card.router, tags=["Virtual Card"])
api_router.include_router(delete_card.router, tags=["Virtual Card"])
api_router.include_router(block.router, tags=["Virtual Card"])
api_router.include_router(topup.router, tags=["Virtual Card"])

# ? AI transaction analysis and fraud detection
api_router.include_router(fraud_review.router, tags=["Fraud Detection"])
api_router.include_router(risk_history.router, tags=["Fraud Detection"])

# ? Machine Learing
api_router.include_router(api.router, tags=["Machine Learning"])
