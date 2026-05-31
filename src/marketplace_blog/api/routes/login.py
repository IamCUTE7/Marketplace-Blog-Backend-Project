from datetime import timedelta
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from marketplace_blog.core.config import get_settings
from marketplace_blog.core.hashing import (
    Hasher,
)
from marketplace_blog.core.security import (
    create_access_token,
)
from marketplace_blog.db.session import (
    get_db,
)
from marketplace_blog.repositories.users import (
    UserRepository,
)
from marketplace_blog.schemas.token import (
    Token,
)
from marketplace_blog.schemas.user import UserRead

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

settings = get_settings()
login_router = APIRouter()


async def authenticate_user(email: str, password: str, db: AsyncSession):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email=email)

    if user is None:
        return None

    if not Hasher.verify_password(password, user.hashed_password):
        return None

    return user


@login_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(
        email=form_data.username, password=form_data.password, db=db
    )

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        user_id = UUID(payload.get("sub"))

        if user_id is None:
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err

    user_repo = UserRepository(db)

    user = await user_repo.get_user_by_id(user_id=user_id)

    if user is None:
        raise credentials_exception

    return user


@login_router.get("/me", response_model=UserRead)
async def get_me(current_user=Depends(get_current_user_from_token)):
    return UserRead.model_validate(current_user)
