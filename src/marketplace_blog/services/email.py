from loguru import logger

from marketplace_blog.core.config import get_settings

settings = get_settings()


async def send_registration_email(email: str) -> None:
    logger.info("Sending email to {}", email)
    print(f"[EMAIL STUB] Registration email sent to {email}")
    logger.info("Email sent to {}", email)
