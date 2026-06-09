from fastapi_mail import MessageSchema, MessageType, MultipartSubtypeEnum

from ...core.celery_app import celery_app
import asyncio
from ...core.logging import get_logger
from .config import fastmail

logger = get_logger()


@celery_app.task(
    name="send_email_task",
    # ? means this taks is now gonna have access to the current task instances's attributes and methods
    bind=True,
    max_retries=3,
    soft_time_limit=60,
    # ? retry the request if it raise an exception
    autoretry_for=(Exception,),
    # ? whether to retry if the task raise exceptions
    retry_backoff=True,
    # ? max time the task will wait before retrying
    retry_backoff_max=60,
)
def send_email_task(
    self,
    recipients: list[str],
    subject: str,
    html_content: str,
    plain_content: str,
) -> bool:
    try:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,  # type: ignore
            body=html_content,
            subtype=MessageType.html,
            alternative_body=plain_content,
            multipart_subtype=MultipartSubtypeEnum.alternative,
        )
        asyncio.run(fastmail.send_message(message))
        logger.info(f"Email successfully sent to {recipients} with subject {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: Error: {str(e)}")
        return False
