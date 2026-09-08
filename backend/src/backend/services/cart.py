from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import CartItem
from backend.repository.cart import CartRepository, CartItemRepository
from backend.repository.product import ProductVariationRepository


class CartService:
    def __init__(
            self,
            session: AsyncSession,
            cart_repo: CartRepository,
            cart_item_repo: CartItemRepository,
            variant_repo: ProductVariationRepository
    ):
        self.cart_repo = cart_repo
        self.cart_item_repo = cart_item_repo
        self.session = session
        self.variant_repo = variant_repo

    async def get_cart(self, user_id: UUID):
        cart = await self.cart_repo.get_or_create(user_id)
        await self.session.commit()
        await self.session.refresh(cart)
        return cart

    async def add_item(
            self,
            user_id: UUID,
            variant_id: UUID,
            quantity: int
    ):
        variant = await self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found")
        cart = await self.cart_repo.get_or_create(user_id)
        existing = await self.cart_item_repo.get_by_cart_and_variant(cart.id, variant_id)
        new_quantity = quantity + (existing.quantity if existing else 0)

        if new_quantity > variant.stock_quantity:
            raise HTTPException(status_code=409, detail="Quantity exceeded")

        if existing:
            existing.quantity = new_quantity
            await self.cart_item_repo.update(existing)
        else:
            await self.cart_item_repo.add(
                CartItem(
                    quantity=new_quantity,
                    variant_id=variant_id,
                    cart_id=cart.id
                )
            )
        await self.session.commit()
        await self.session.refresh(cart)
        return cart

    async def update_item(
            self,
            user_id: UUID,
            variant_id: UUID,
            quantity: int
    ):
        variant = await self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found")
        cart = await self.cart_repo.get_or_create(user_id)
        existing = await self.cart_item_repo.get_by_cart_and_variant(cart.id, variant_id)
        if not existing:
            raise HTTPException(status_code=400, detail="Product not in the cart")
        new_quantity = quantity + existing.quantity
        if new_quantity > variant.stock_quantity:
            raise HTTPException(status_code=409, detail="Quantity exceeded")
        existing.quantity = new_quantity
        await self.cart_item_repo.update(existing)
        await self.session.commit()

    async def remove_item(
            self,
            user_id: UUID,
            variant_id: UUID,
    ):
        variant = await self.variant_repo.get_by_id(variant_id)
        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found")
        cart = await self.cart_repo.get_or_create(user_id)
        existing = await self.cart_item_repo.get_by_cart_and_variant(cart.id, variant_id)  # CartItem | None
        if existing:
            cart.items.remove(existing)
        await self.session.commit()

    async def clear_cart(
            self,
            user_id: UUID
    ):
        cart = await self.cart_repo.get_or_create(user_id)
        cart.items.clear()
        await self.session.commit()
