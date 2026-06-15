from fastapi import APIRouter, HTTPException, Response, status

from ....auth.schema import LoginRequestSchema, OTPVerifyRequestSchema
from ....auth.utils import create_jwt_token, set_auth_cookies
from ....core.config import settings
from ....core.logging import get_logger
from .deps import SessionDep
from ...services.user_auth import user_auth_service

logger = get_logger()

router = APIRouter(prefix="/auth")


@router.post("/login/request-otp", status_code=status.HTTP_200_OK)
async def request_login_otp(
    login_data: LoginRequestSchema,
    session: SessionDep,
):
    try:
        user = await user_auth_service.get_user_by_email(login_data.email, session)

        if user:
            await user_auth_service.check_user_lockout(user, session)

            if not await user_auth_service.verity_user_password(
                login_data.password, user.hashed_password
            ):
                await user_auth_service.increment_failed_login_attempts(user, session)
                remaining_attempts = (
                    settings.LOGIN_ATTEMPTS - user.failed_login_attempts
                )

                if remaining_attempts > 0:
                    error_message = (
                        f"Invalid credentials. You have {remaining_attempts}"
                        f"attempt{'s' if remaining_attempts != 1 else ''} remaining before your account is temporarily locked"
                    )
                else:
                    error_message = (
                        "Invalid credentials. Your account has been temporarily locked due "
                        f"to too many failed attempts. Please try again after {settings.LOGOUT_DURATION_MINUTES} minutes"
                    )

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "status": "error",
                        "message": error_message,
                        "action": "Please check your email and password and try agian",
                        "remaining_attempts": remaining_attempts,
                    },
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "error",
                        "message": "Your account is not activated",
                        "action": "Please activate your account first",
                    },
                )

            await user_auth_service.reset_user_state(
                user, session, clear_otp=True, log_action=True
            )

            await user_auth_service.generate_and_save_otp(user, session)

        return {
            "message": "If an account exits with this email, an OTP has been sent to it"
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to process login OTP request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to process login OTP request",
            },
        )


@router.post("/login/verify-otp", status_code=status.HTTP_200_OK)
async def verfity_login_otp(
    verify_data: OTPVerifyRequestSchema,
    response: Response,
    session: SessionDep,
):
    try:
        user = await user_auth_service.verify_login_otp(
            verify_data.email, verify_data.otp, session
        )
        await user_auth_service.reset_user_state(
            user, session, clear_otp=True, log_action=True
        )

        access_token = create_jwt_token(user.id)
        refresh_token = create_jwt_token(user.id, type=settings.COOKIE_REFRESH_NAME)
        set_auth_cookies(response, access_token, refresh_token)

        return {
            "message": "Login successful",
            "user": {
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.full_name,
                "id_no": user.id_no,
                "role": user.role,
            },
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to verify login OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to verity OTP",
                "action": "Please try again later",
            },
        )
