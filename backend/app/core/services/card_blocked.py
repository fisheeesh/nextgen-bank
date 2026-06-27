from datetime import datetime
from ..config import settings
from ..emails.base import EmailTemplate


class VirtualCardBlockedEmail(EmailTemplate):
    template_name = "card_blocked.html"
    template_name_plain = "card_blocked.txt"
    subject = "Your Virtual Card Has been Blocked"


async def send_card_created_email(
    email: str,
    full_name: str,
    card_type: str,
    masked_card_number: str,
    blocked_reason: str,
    blocked_reason_description: str,
    blocked_at: datetime,
) -> None:
    context = {
        "full_name": full_name,
        "card_type": card_type,
        "maksed_card_number": masked_card_number,
        "blocked_reason": blocked_reason,
        "blocked_reason_description": blocked_reason_description,
        "site_name": settings.SITE_NAME,
        "support_email": settings.SUPPORT_EMAIL,
        "blocked_at": blocked_at.strftime("%Y-%m%-d %H:%M:%S UTC"),
    }

    await VirtualCardBlockedEmail.send_email(email_to=email, context=context)
