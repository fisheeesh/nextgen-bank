from fastapi import APIRouter

from .routes import home
from .routes.auth import activate, login, password_reset, refresh, register, logout
from .routes.profile import create

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
