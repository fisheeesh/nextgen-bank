from fastapi import APIRouter
from .routes import home
from .routes.auth import register, activate, login

api_router = APIRouter()

api_router.include_router(home.router)
api_router.include_router(register.router)
api_router.include_router(activate.router)
api_router.include_router(login.router)
