from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, String, Numeric, CheckConstraint, Table, Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import Base
from backend.models.mixins import TimeStampMixin, LanguageMixin

variant_attribute_values = Table(
    "variant_attribute_values",
    Base.metadata,
    Column("variant_id", ForeignKey("product_variations.id", ondelete="CASCADE"), primary_key=True),
    Column("attribute_value_id", ForeignKey("attribute_values.id", ondelete="CASCADE"), primary_key=True),
)


class Product(TimeStampMixin, Base):
    __tablename__ = "products"

    shop_id: Mapped[UUID] = mapped_column(
        ForeignKey("shops.id"),
    )
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )

    translations: Mapped[list["ProductTranslation"]] = relationship(
        back_populates="product"
    )
    variations: Mapped[list["ProductVariation"]] = relationship(
        back_populates="product",
        lazy="selectin"
    )
    shop: Mapped["Shop"] = relationship(
        back_populates="products"
    )

    @hybrid_property
    def price_from(self) -> Decimal:
        min_price = min(v.price for v in self.variations)
        return Decimal(min_price)

    @hybrid_property
    def price_to(self) -> Decimal:
        max_price = max(v.price for v in self.variations)
        return Decimal(max_price)


class ProductTranslation(LanguageMixin, Base):
    __tablename__ = "product_translations"

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id"),
    )
    name: Mapped[str] = mapped_column(
        String(320)
    )
    description: Mapped[str | None] = mapped_column(
        String(2048)
    )

    product: Mapped[Product] = relationship(
        back_populates="translations"
    )


class ProductVariation(Base):
    __tablename__ = "product_variations"
    __table_args__ = (
        CheckConstraint("price > 0"),
        CheckConstraint("stock_quantity >= 0"),
    )

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id"),
    )
    sku: Mapped[str] = mapped_column(
        String(320)
    )
    price: Mapped[float] = mapped_column(
        Numeric(12, 2)
    )
    stock_quantity: Mapped[int] = mapped_column(default=0)
    sold_count: Mapped[int] = mapped_column(default=0)

    product: Mapped[Product] = relationship(
        back_populates="variations"
    )
    attribute_values: Mapped[list["AttributeValue"]] = relationship(
        secondary=variant_attribute_values,
        back_populates="variations"
    )


class Attribute(Base):
    __tablename__ = "attributes"

    translations: Mapped[list["AttributeTranslation"]] = relationship(
        back_populates="attribute"
    )
    values: Mapped[list["AttributeValue"]] = relationship(
        back_populates="attribute"
    )


class AttributeTranslation(LanguageMixin, Base):
    __tablename__ = "attribute_translations"

    attribute_id: Mapped[UUID] = mapped_column(
        ForeignKey("attributes.id"),
    )
    name: Mapped[str] = mapped_column(
        String(320)
    )

    attribute: Mapped["Attribute"] = relationship(
        back_populates="translations"
    )


class AttributeValue(Base):
    __tablename__ = "attribute_values"

    attribute_id: Mapped[UUID] = mapped_column(
        ForeignKey("attributes.id"),
    )

    attribute: Mapped["Attribute"] = relationship(
        back_populates="values"
    )
    translations: Mapped[list["AttributeValueTranslation"]] = relationship(
        back_populates="attribute_value"
    )
    variations: Mapped[list["ProductVariation"]] = relationship(
        secondary=variant_attribute_values,
        back_populates="attribute_values"
    )


class AttributeValueTranslation(LanguageMixin, Base):
    __tablename__ = "attribute_value_translations"

    attribute_value_id: Mapped[UUID] = mapped_column(
        ForeignKey("attribute_values.id"),
    )
    value: Mapped[str] = mapped_column(
        String(320)
    )
    attribute_value: Mapped["AttributeValue"] = relationship(
        back_populates="translations"
    )

# Кросовки #1 sku=NIKE-RED-41 color=RED size=41
# Кросовки #2 sku=NIKE-RED-42 color=RED size=42
