from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from backend.core.security import decode_token
from backend.dependencies.database import SessionDep
from backend.dependencies.shop import ShopRepoDep
from backend.models import User
from backend.repository.user import UserRepository
from backend.services.auth import AuthService


async def get_user_repo(
        session: SessionDep
) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[
    UserRepository,
    Depends(get_user_repo)
]


async def get_auth_service(
        session: SessionDep,
        user_repo: UserRepoDep,
        shop_repo: ShopRepoDep
) -> AuthService:
    return AuthService(
        session=session,
        user_repo=user_repo,
        shop_repo=shop_repo
    )


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service)
]

oauth2_scheme = HTTPBearer()


async def get_current_user(
        user_repo: UserRepoDep,
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> User:
    user_id = decode_token(
        credentials.credentials,
    )
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Credentials",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive User",
        )
    return user


CurrentUserDep = Annotated[
    User,
    Depends(get_current_user)
]
