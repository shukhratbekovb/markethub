from uuid import UUID

from sqlalchemy import select, Select, and_, func, update
from sqlalchemy.orm import selectinload, contains_eager

from backend.core.enums import LanguageEnum
from backend.models import Product, ProductVariation, Attribute, AttributeValue, ProductTranslation
from backend.repository.base import BaseRepository
from backend.repository.mixins import AddRepositoryMixin, RetrieveRepositoryMixin, UpdateRepositoryMixin, \
    ListRepositoryMixin, PaginatedListRepositoryMixin, T
from backend.schemas.filters import BaseFilter
from backend.schemas.pagination import PaginationParams, Page

VARIANT_LOAD_OPTIONS = (
    selectinload(ProductVariation.attribute_values).selectinload(AttributeValue.translations),
    selectinload(ProductVariation.attribute_values)
    .selectinload(AttributeValue.attribute)
    .selectinload(Attribute.translations),
)

_price_from_subq = (
    select(func.min(ProductVariation.price))
    .where(ProductVariation.product_id == Product.id)
    .correlate(Product)
    .scalar_subquery()
    .label("price_from")
)
_price_to_subq = (
    select(func.max(ProductVariation.price))
    .where(ProductVariation.product_id == Product.id)
    .correlate(Product)
    .scalar_subquery()
    .label("price_to")
)


class ProductRepository(
    AddRepositoryMixin[Product],
    RetrieveRepositoryMixin[Product],
    UpdateRepositoryMixin[Product],
    ListRepositoryMixin[Product],
    PaginatedListRepositoryMixin[Product],
    BaseRepository
):
    model = Product
    base_query = select(Product).options(selectinload(Product.translations))

    def query_for_language(self, lang: LanguageEnum) -> Select:
        return (
            select(Product, _price_from_subq, _price_to_subq)
            .join(
                ProductTranslation,
                and_(
                    ProductTranslation.product_id == Product.id,
                    ProductTranslation.lang == lang,
                ),
            )
            .options(contains_eager(Product.translations))
            .where(Product.is_active.is_(True), _price_from_subq.isnot(None))
        )

    async def list_paginated(
            self,
            pagination: PaginationParams,
            filters: BaseFilter | None = None,
            lang: LanguageEnum = LanguageEnum.RUSSIAN,
    ) -> Page[T]:
        stmt = filters.sort(filters.filter(self.query_for_language(lang)))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        result = await self.session.execute(stmt)
        rows = result.unique().all()  # каждая строка: (Product, price_from, price_to)

        return Page.create(items=rows, total=total, params=pagination)


class ProductVariationRepository(
    AddRepositoryMixin[ProductVariation],
    RetrieveRepositoryMixin[ProductVariation],
    UpdateRepositoryMixin[ProductVariation],
    ListRepositoryMixin[ProductVariation],
    BaseRepository
):
    model = ProductVariation
    base_query = select(ProductVariation).options(
        *VARIANT_LOAD_OPTIONS
    )

    async def list_by_product(
            self,
            product_id: UUID
    ):
        stmt = self.base_query.where(ProductVariation.product_id == product_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_attribute_values(self, attribute_value_ids: list):
        stmt = select(AttributeValue).where(AttributeValue.id.in_(attribute_value_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def adjust_stock(self, variant_id: UUID, delta: int):
        stmt = (
            update(ProductVariation)
            .where(
                ProductVariation.id == variant_id, ProductVariation.stock_quantity + delta >= 0
            )
            .values(
                stock_quantity=ProductVariation.stock_quantity + delta
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()


class AttributeRepository(
    AddRepositoryMixin[Attribute],
    RetrieveRepositoryMixin[Attribute],
    UpdateRepositoryMixin[Attribute],
    ListRepositoryMixin[Attribute],
    BaseRepository
):
    model = Attribute
