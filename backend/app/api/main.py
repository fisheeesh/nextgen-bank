from fastapi import APIRouter
from .routes import home
from .routes.auth import register, activate

api_router = APIRouter()

api_router.include_router(home.router)
api_router.include_router(register.router)
api_router.include_router(activate.router)
