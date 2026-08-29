import enum
from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Enum, Numeric, Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.models import Base
from backend.models.mixins import TimeStampMixin


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(TimeStampMixin, Base):
    __tablename__ = 'orders'

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False), default=OrderStatus.PENDING
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))


class OrderItem(TimeStampMixin, Base):
    __tablename__ = 'order_items'
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_item_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_order_item_unit_price_positive"),
    )

    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    variant_id: Mapped[UUID] = mapped_column(ForeignKey("product_variations.id"))
    product_name_snapshot: Mapped[str] = mapped_column(String(255))
    variant_label_snapshot: Mapped[str | None] = mapped_column(String(500))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantity: Mapped[int] = mapped_column(Integer)
