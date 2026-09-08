from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.core.configs import settings
from backend.core.enums import LanguageEnum
from backend.core.i18n import resolve_translation
from backend.models import OrderItem, CartItem, ProductVariation, Order
from backend.models.order import OrderStatus
from backend.repository.cart import CartRepository, CartItemRepository
from backend.repository.order import OrderRepository
from backend.repository.product import ProductVariationRepository


class OrderService:
    def __init__(
            self,
            session: AsyncSession,
            order_repo: OrderRepository,
            cart_repo: CartRepository,
            cart_item_repo: CartItemRepository,
            variant_repo: ProductVariationRepository
    ):
        self.session = session
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.cart_item_repo = cart_item_repo
        self.variant_repo = variant_repo

    async def create_order(
            self,
            user_id: UUID,
            lang: LanguageEnum,
    ):
        cart = await self.cart_repo.get_for_checkout(user_id)

        if cart is None or not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )
        order_items: list[OrderItem] = []
        total = Decimal("0")

        for cart_item in cart.items:
            order_item = await self._reserve_and_snapshot(cart_item, lang)
            order_items.append(order_item)
            total += order_item.unit_price * order_item.quantity

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total,
            items=order_items,
        )
        await self.order_repo.add(order)

        for cart_item in cart.items:
            await self.cart_item_repo.delete(cart_item)

        await self.session.commit()

    async def _reserve_and_snapshot(self, cart_item: CartItem, lang: LanguageEnum):
        variant = cart_item.variant
        # склад - n кол-во товара
        return OrderItem(
            variant_id=variant.id,
            product_name_snapshot=self._product_name(variant, lang),
            variant_label_snapshot=self._variant_label(variant, lang),
            unit_price=variant.price,
            quantity=cart_item.quantity,
        )

    def _product_name(self, variant: ProductVariation, lang: LanguageEnum) -> str:
        translation = resolve_translation(variant.product.translations, lang, settings.default_language)
        return translation.name if translation else variant.sku

    def _variant_label(self, variant: ProductVariation, lang: LanguageEnum) -> str:
        if not variant.attribute_values:
            return ""
        parts = []
        for value in variant.attribute_values:
            attr_t = resolve_translation(value.attribute.translations, lang, settings.default_language)
            value_t = resolve_translation(value.translations, lang, settings.default_language)
            if attr_t and value_t:
                parts.append(f"{attr_t.name}: {value_t.name}")
        return ", ".join(parts)
