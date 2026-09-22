import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import hash_password
from backend.models import User
from backend.repository.user import UserRepository
from backend.schemas.auth import RegisterUser


async def create_admin():
    first_name: str = input("Enter your first name: ")
    last_name: str = input("Enter your last name: ")
    username: str = input("Enter your username: ")
    email: str = input("Email: ")
    password: str = input("Password: ")

    body = RegisterUser(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )
    async with AsyncSession() as session:
        user_repo = UserRepository(
            session=session,
        )

        exist_user = await user_repo.get_by_email(body.email)
        if exist_user is not None:
            raise Exception(
                "Email already registered",
            )

        exists_username = await user_repo.get_by_username(username)
        if exists_username is not None:
            raise Exception(
                "Username already registered",
            )
        hashed_password = hash_password(password)
        user = User(
            username=username,
            hashed_password=hashed_password,
            **body.model_dump(exclude={"password"})
        )
        await user_repo.add(user)
        await session.commit()
    print(f"Admin {username} successfully created")

if __name__ == '__main__':
    asyncio.run(create_admin())