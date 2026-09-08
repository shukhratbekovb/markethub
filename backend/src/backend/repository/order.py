from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models import Order, OrderItem
from backend.repository.base import BaseRepository
from backend.repository.mixins import AddRepositoryMixin, RetrieveRepositoryMixin, UpdateRepositoryMixin, \
    DeleteRepositoryMixin


class OrderRepository(
    AddRepositoryMixin[Order],
    RetrieveRepositoryMixin[Order],
    UpdateRepositoryMixin[Order],
    DeleteRepositoryMixin[Order],
    BaseRepository
):
    model = Order
    base_query = select(Order).options(
        selectinload(Order.items).selectinload(OrderItem.variant)
    )
