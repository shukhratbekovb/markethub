import asyncio

from passlib.handlers.argon2 import argon2

from backend.core.database import SessionFactory
from backend.models import User
from backend.models.user import UserRole


async def create_user():
    async with SessionFactory() as session:
        user = User(
            first_name='Admin',
            last_name='User',
            email='test@example.com',
            username="test",
            hashed_password=argon2.hash("password"),
            role=UserRole.SELLER
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(user.id)

asyncio.run(create_user())