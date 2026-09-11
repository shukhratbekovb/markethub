from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.handlers.argon2 import argon2
from password_validator import PasswordValidator
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.core.configs import settings
from backend.models import User

password_schema = PasswordValidator()

password_schema \
    .max(320) \
    .min(8) \
    .has().uppercase() \
    .has().lowercase() \
    .has().digits() \
    .has().symbols()


async def generate_username(
        session: AsyncSession,
        first_name: str,
        last_name: str,
) -> str:
    variants = [
        slugify(f"{last_name}", separator="_"),  # tyo
        slugify(f"{first_name[0]} {last_name}", separator="_"),  # v_tyo
        slugify(f"{first_name} {last_name}", separator="_"),  # vladislav_tyo
    ]

    for variant in variants:
        stmt = select(User).where(User.username == variant)
        result = await session.execute(stmt)
        if result.scalar_one_or_none() is None:
            return variant

    base_variant = variants[0]
    counter = 1

    while True:
        fallback_variant = f"{base_variant}_{counter}"
        stmt = select(User).where(User.username == fallback_variant)
        result = await session.execute(stmt)
        if result.scalar_one_or_none() is None:
            return fallback_variant
        counter += 1


def hash_password(password: str) -> str:
    return argon2.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return argon2.verify(password, hashed_password)

def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )


def create_refresh_token(user_id: UUID) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )


def decode_token(token: str, expected: str = "access") -> UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id_str: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if user_id_str is None or token_type != expected:
            raise credentials_exception
    except JWTError as e:
        print(e)
        raise credentials_exception

    return UUID(user_id_str)
