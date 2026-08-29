from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Select, select

from backend.models import Product, ProductTranslation, ProductVariation
from backend.schemas.filters import BaseFilter
from backend.schemas.translation import TranslationSchema, LANGUAGES


class AttributeTranslationSchema(TranslationSchema):
    name: str = Field(max_length=320)


class AttributeCreate(BaseModel):
    translations: list[AttributeTranslationSchema]

    @field_validator("translations", mode="after")
    @classmethod
    def validate_translations(cls, v: list[ProductTranslationCreate]):
        languages = [t.lang for t in v]
        if frozenset(languages) != LANGUAGES:
            raise ValueError("Не указан один из языков")
        return v


class AttributeResponse(BaseModel):
    id: UUID
    name: str


class AttributeValueTranslationSchema(TranslationSchema):
    value: str = Field(max_length=320)


class AttributeValueCreate(BaseModel):
    translations: list[AttributeValueTranslationSchema]

    @field_validator("translations", mode="after")
    @classmethod
    def validate_translations(cls, v: list[ProductTranslationCreate]):
        languages = [t.lang for t in v]
        if frozenset(languages) != LANGUAGES:
            raise ValueError("Не указан один из языков")
        return v


class AttributeValueResponse(BaseModel):
    id: UUID
    value: str


class ProductVariantCreate(BaseModel):
    sku: str
    price: Decimal
    stock_quantity: int = Field(ge=0, default=0)
    attribute_value_ids: list[UUID] = []


class VariantAttributeResponse(BaseModel):
    attribute: str
    value: str


class ProductVariationResponse(BaseModel):
    id: UUID
    sku: str
    price: Decimal
    stock_quantity: int
    attributes: list[VariantAttributeResponse]


class ProductTranslationCreate(TranslationSchema):
    name: str = Field(min_length=3, max_length=320)
    description: str | None = Field(default=None, max_length=2048)


class ProductCreate(BaseModel):
    shop_id: UUID
    category_id: UUID
    translations: list[ProductTranslationCreate]

    @field_validator("translations", mode="after")
    @classmethod
    def validate_translations(cls, v: list[ProductTranslationCreate]):
        languages = [t.lang for t in v]
        if frozenset(languages) != LANGUAGES:
            raise ValueError("Не указан один из языков")
        return v


class ProductCreateResponse(BaseModel):
    id: UUID


class ProductUpdate(BaseModel):
    translations: list[ProductTranslationCreate]

    @field_validator("translations", mode="after")
    @classmethod
    def validate_translations(cls, v: list[ProductTranslationCreate]):
        languages = [t.lang for t in v]
        if frozenset(languages) != LANGUAGES:
            raise ValueError("Не указан один из языков")
        return v


class ProductBrief(BaseModel):
    id: UUID
    name: str
    # рейтинг
    price_from: Decimal
    price_to: Decimal
    # изображение
    created_at: datetime


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    category_id: UUID
    shop_id: UUID

    # изображения
    variants: list[ProductVariationResponse] = []


class ProductSort(str, Enum):
    created_at_asc = "created_at:asc"
    created_at_desc = "created_at:desc"


_PRODUCT_SORT_COLUMN = {
    ProductSort.created_at_asc: Product.created_at.asc(),
    ProductSort.created_at_desc: Product.created_at.desc(),
}


@dataclass
class ProductFilter(BaseFilter):
    category_id: UUID | None = None
    shop_id: UUID | None = None
    search: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    sort_by: ProductSort = ProductSort.created_at_asc

    def filter(
            self,
            stmt: Select,
    ) -> Select:
        if self.category_id is not None:
            stmt = stmt.where(Product.category_id == self.category_id)

        if self.shop_id is not None:
            stmt = stmt.where(Product.shop_id == self.shop_id)

        if self.search is not None:
            stmt = stmt.where(ProductTranslation.name.ilike(f"%{self.search}%"))

        if self.min_price is not None or self.max_price is not None:
            price_exists = select(ProductVariation.id).where(
                ProductVariation.product_id == Product.id
            )
            if self.min_price is not None:
                price_exists = price_exists.where(ProductVariation.price >= self.min_price)
            if self.max_price is not None:
                price_exists = price_exists.where(ProductVariation.price <= self.max_price)
            stmt = stmt.where(price_exists.exists())

        return stmt

    def sort(
            self,
            stmt: Select
    ) -> Select:
        sort_column = _PRODUCT_SORT_COLUMN.get(self.sort_by)
        if sort_column is not None:
            return stmt
        return stmt.order_by(sort_column)

class StockAdjustRequest(BaseModel):
    delta: int

class StockSetRequest(BaseModel):
    stock_quantity: int = Field(ge=0)