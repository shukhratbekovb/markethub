from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.configs import settings
from backend.core.enums import LanguageEnum
from backend.core.i18n import resolve_translation
from backend.models import Product, ProductTranslation, ProductVariation
from backend.repository.product import ProductRepository, ProductVariationRepository
from backend.schemas.pagination import PaginationParams, Page
from backend.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductBrief,
    ProductVariationResponse,
    VariantAttributeResponse,
    ProductVariantCreate, ProductUpdate, ProductFilter, StockAdjustRequest, StockSetRequest
)


class ProductService:
    def __init__(
            self,
            session: AsyncSession,
            product_repo: ProductRepository,
            product_variant_repo: ProductVariationRepository
    ):
        self.session = session
        self.product_repo = product_repo
        self.product_variant_repo = product_variant_repo

    async def add_variant(
            self,
            product: Product,
            body: ProductVariantCreate,
    ):
        attribute_values = await self.product_variant_repo.get_attribute_values(body.attribute_value_ids)
        variant = ProductVariation(
            product_id=product.id,
            price=body.price,
            sku=body.sku,
            stock_quantity=body.stock_quantity,
            attribute_values=attribute_values
        )

        await self.product_variant_repo.add(variant)
        await self.session.commit()

    async def list_variants(
            self,
            product_id: UUID,
            lang: LanguageEnum = LanguageEnum.RUSSIAN
    ):
        variants = await self.product_variant_repo.list_by_product(product_id)
        return [self._to_variant_response(v, lang) for v in variants]

    async def adjust_stock(
            self,
            variant: ProductVariation,
            body: StockAdjustRequest
    ):
        await self.product_variant_repo.adjust_stock(variant.id, body.delta)
        await self.session.commit()

    async def set_stock(
            self,
            variant: ProductVariation,
            body: StockSetRequest
    ):
        variant.stock_quantity = body.stock_quantity
        await self.product_variant_repo.update(variant)
        await self.session.commit()

    def _to_variant_response(
            self,
            variant: ProductVariation,
            lang: LanguageEnum = LanguageEnum.RUSSIAN
    ) -> ProductVariationResponse:
        attributes = []
        for value in variant.attribute_values:
            attr_translation = resolve_translation(value.attribute.translations, lang, settings.default_language)
            value_translation = resolve_translation(value.translations, lang, settings.default_language)
            attributes.append(
                VariantAttributeResponse(
                    attribute=attr_translation.name if attr_translation else "",
                    value=value_translation.value if value_translation else "",
                )
            )
        return ProductVariationResponse(
            id=variant.id,
            sku=variant.sku,
            price=Decimal(variant.price),
            stock_quantity=variant.stock_quantity,
            attributes=attributes
        )

    async def create_product(
            self,
            body: ProductCreate,
    ) -> Product:
        product = Product(
            shop_id=body.shop_id,
            category_id=body.category_id,
            translations=[
                ProductTranslation(
                    name=t.name,
                    description=t.description,
                    lang=t.lang
                )
                for t in body.translations
            ]
        )

        await self.product_repo.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def get_product(
            self,
            product_id: UUID,
            lang: LanguageEnum = LanguageEnum.RUSSIAN
    ):
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        translation = resolve_translation(
            translations=product.translations,
            lang=lang,
            default_lang=LanguageEnum.RUSSIAN
        )

        if not translation:
            raise HTTPException(status_code=404, detail="Product not found")

        variants = []

        for variant in product.variations:
            attributes = []
            for av in variant.attribute_values:
                attr = av.attribute
                attribute = resolve_translation(
                    translations=attr.translations,
                    lang=lang,
                    default_lang=LanguageEnum.RUSSIAN
                )
                value = resolve_translation(
                    translations=av.translations,
                    lang=lang,
                    default_lang=LanguageEnum.RUSSIAN
                )
                attributes.append(
                    VariantAttributeResponse(
                        attribute=attribute,
                        value=value
                    )
                )

            variants.append(
                ProductVariationResponse(
                    id=variant.id,
                    sku=variant.sku,
                    price=variant.price,
                    stock_quantity=variant.stock_quantity,
                    attributes=attributes
                )
            )

        return ProductResponse(
            id=product.id,
            shop_id=product.shop_id,
            category_id=product.category_id,
            name=translation.name,
            description=translation.description,
            variants=variants
        )

    async def update_product(
            self,
            product: Product,
            body: ProductUpdate,
    ) -> None:
        translations = body.translations
        for pt in product.translations:
            for t in translations:
                if t.lang == pt.lang:
                    pt.name = t.name
                    pt.description = t.description
        await self.product_repo.update(product)
        await self.session.commit()

    async def delete_product(
            self,
            product: Product
    ) -> None:
        # Safe Delete
        product.is_active = False
        await self.product_repo.update(product)
        await self.session.commit()

    async def list_paginated_products(
            self,
            pagination: PaginationParams,
            filters: ProductFilter,
            lang: LanguageEnum = LanguageEnum.RUSSIAN,
    ):
        page = await self.product_repo.list_paginated(pagination, filters, lang)
        items = [
            ProductBrief(
                id=product.id,
                name=resolve_translation(product.translations, lang, settings.default_language).name,
                price_from=price_from,
                price_to=price_to,
                created_at=product.created_at,
            )
            for product, price_from, price_to in page.items
        ]
        return Page(
            items=items, total=page.total, page=page.page, size=page.size,
            pages=page.pages, has_next=page.has_next, has_prev=page.has_prev,
        )
