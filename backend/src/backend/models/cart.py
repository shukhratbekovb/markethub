from uuid import UUID

from sqlalchemy import ForeignKey, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import Base
from backend.models.mixins import TimeStampMixin

# 1 to 1
class Cart(TimeStampMixin, Base):
    __tablename__ = 'carts'

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart",
    )

class CartItem(TimeStampMixin, Base):
    __tablename__ = 'cart_items'
    __table_args__ = (
        UniqueConstraint("cart_id", "variant_id"),
        CheckConstraint("quantity > 0", name="ck_cart_item_quantity_positive"),
    )

    cart_id: Mapped[UUID] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"))
    variant_id: Mapped[UUID] = mapped_column(ForeignKey("product_variations.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer)

    cart: Mapped[Cart] = relationship(
        back_populates="items",
    )

    variant: Mapped["ProductVariation"] = relationship(
        backref="items",
    )

