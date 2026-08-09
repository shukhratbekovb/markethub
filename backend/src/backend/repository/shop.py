from backend.models import Shop
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    PaginatedListRepositoryMixin,
    ListRepositoryMixin,
    DeleteRepositoryMixin,
    UpdateRepositoryMixin,
    RetrieveRepositoryMixin
)


class ShopRepository(
    AddRepositoryMixin[Shop],
    RetrieveRepositoryMixin[Shop],
    UpdateRepositoryMixin[Shop],
    DeleteRepositoryMixin[Shop],
    ListRepositoryMixin[Shop],
    PaginatedListRepositoryMixin[Shop],
    BaseRepository
):
    pass
