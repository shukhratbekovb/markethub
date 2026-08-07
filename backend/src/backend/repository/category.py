from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models import Category
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    UpdateRepositoryMixin,
    DeleteRepositoryMixin,
    RetrieveRepositoryMixin,
    ListRepositoryMixin,
    PaginatedListRepositoryMixin
)


class CategoryRepository(
    AddRepositoryMixin[Category],
    RetrieveRepositoryMixin[Category],
    UpdateRepositoryMixin[Category],
    DeleteRepositoryMixin[Category],
    ListRepositoryMixin[Category],
    PaginatedListRepositoryMixin[Category],
    BaseRepository
):
    base_query = select(Category).options(
        selectinload(Category.translations)
    )

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = self.base_query.where(self.model.id == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

