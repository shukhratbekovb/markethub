from sqlalchemy import select

from backend.models import User
from backend.repository.base import BaseRepository
from backend.repository.mixins import AddRepositoryMixin, RetrieveRepositoryMixin, UpdateRepositoryMixin, \
    DeleteRepositoryMixin


class UserRepository(
    AddRepositoryMixin[User],
    RetrieveRepositoryMixin[User],
    UpdateRepositoryMixin[User],
    DeleteRepositoryMixin[User],
    BaseRepository
):
    model = User
    base_query = select(User)

    async def get_by_username(
            self, username: str
    ) -> User | None:
        stmt = self.base_query.where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(
            self, email: str
    ) -> User | None:
        stmt = self.base_query.where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
