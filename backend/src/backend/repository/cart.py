from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models import Cart, CartItem, ProductVariation, Product
from backend.repository.base import BaseRepository
from backend.repository.mixins import AddRepositoryMixin, RetrieveRepositoryMixin, UpdateRepositoryMixin, \
    DeleteRepositoryMixin
from backend.repository.product import VARIANT_LOAD_OPTIONS


class CartRepository(
    AddRepositoryMixin[Cart],
    RetrieveRepositoryMixin[Cart],
    BaseRepository
):
    model = Cart
    base_query = select(Cart).options(
        selectinload(Cart.items).selectinload(CartItem.variant)
    )

    async def get_by_user(self, user_id: UUID) -> Cart | None:
        stmt = self.base_query.where(Cart.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: UUID) -> Cart:
        cart = await self.get_by_user(user_id)
        if cart is not None:
            return cart
        return await self.add(Cart(user_id=user_id))

    def _checkout_query(self):
        return select(Cart).options(
            selectinload(Cart.items).selectinload(CartItem.variant).options(
                selectinload(ProductVariation.product).selectinload(Product.translations),
                *VARIANT_LOAD_OPTIONS
            )
        )

    async def get_for_checkout(self, user_id: UUID) -> Cart | None:
        stmt = self._checkout_query().where(Cart.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class CartItemRepository(
    AddRepositoryMixin[CartItem],
    RetrieveRepositoryMixin[CartItem],
    UpdateRepositoryMixin[CartItem],
    DeleteRepositoryMixin[CartItem],
    BaseRepository
):
    model = CartItem
    base_query = select(CartItem)

    async def get_by_cart_and_variant(self, cart_id: UUID, variant_id: UUID) -> CartItem | None:
        stmt = select(CartItem).where(CartItem.cart_id == cart_id, CartItem.variant_id == variant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
