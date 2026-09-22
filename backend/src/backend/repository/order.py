from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models import Order, OrderItem, Product, ProductVariation, Shop
from backend.repository.base import BaseRepository
from backend.repository.mixins import AddRepositoryMixin, RetrieveRepositoryMixin, UpdateRepositoryMixin, \
    DeleteRepositoryMixin
from backend.schemas.order import OrderFilter


def has_items_of_seller(
        seller_id: UUID
):
    return (
        select(OrderItem.id)
        .join(ProductVariation, ProductVariation.id == OrderItem.variant_id)
        .join(Product, Product.id == ProductVariation.product_id)
        .join(Shop, Shop.id == Product.shop_id)
        .where(OrderItem.order == Order.id, Shop.owner_id == seller_id)
        .exists()
    )


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

    def _seller_query(
            self,
            seller_id: UUID
    ):
        return (
            select(Order)
            .where(has_items_of_seller(seller_id))
            .options(
                selectinload(Order.items).selectinload(OrderItem.variant).selectinload(ProductVariation.product)
            )
        )

    async def list_customer_orders(
            self,
            user_id: UUID,
            filters: OrderFilter,
    ):
        stmt = filters.filter(self.base_query.where(Order.user_id == user_id))
        stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        orders = result.scalars().all()
        return orders

    async def get_customer_order(
            self,
            user_id: UUID,
            order_id: UUID,
    ):
        stmt = self.base_query.where(Order.user_id == user_id, Order.id == order_id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def list_for_seller(
            self,
            seller_id: UUID,
            filters: OrderFilter,
    ):
        stmt = self._seller_query(seller_id)
        stmt = filters.filter(stmt)
        stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        orders = result.scalars().all()
        return orders

    async def get_for_seller(
            self,
            seller_id: UUID,
            order_id: UUID,
    ):
        stmt = self._seller_query(seller_id).where(Order.id == order_id)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
