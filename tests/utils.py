from datetime import timedelta

from marketplace_blog.core.config import get_settings
from marketplace_blog.core.security import create_access_token

settings = get_settings()


def create_test_auth_headers_for_user(user_id):
    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return {"Authorization": f"Bearer {access_token}"}
