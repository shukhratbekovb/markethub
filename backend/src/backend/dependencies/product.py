from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from backend.dependencies.database import SessionDep
from backend.models import Product, ProductVariation
from backend.repository.product import ProductRepository, ProductVariationRepository
from backend.services.product import ProductService


async def get_product_repo(
        session: SessionDep
) -> ProductRepository:
    return ProductRepository(session)


ProductRepoDep = Annotated[
    ProductRepository,
    Depends(get_product_repo)
]


async def get_product_variant_repo(
        session: SessionDep
) -> ProductVariationRepository:
    return ProductVariationRepository(session)


ProductVariantRepoDep = Annotated[
    ProductVariationRepository,
    Depends(get_product_variant_repo)
]


async def get_product_service(
        session: SessionDep,
        product_repo: ProductRepoDep,
        product_variant_repo: ProductVariantRepoDep
) -> ProductService:
    return ProductService(
        session=session,
        product_repo=product_repo,
        product_variant_repo=product_variant_repo
    )


ProductServiceDep = Annotated[
    ProductService,
    Depends(get_product_service)
]


async def get_current_product(
        product_repo: ProductRepoDep,
        product_id: UUID
) -> Product:
    product = await product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


CurrentProductDep = Annotated[
    Product,
    Depends(get_current_product)
]


async def get_current_product_variant(
        variant_id: UUID,
        product: CurrentProductDep,
        product_variant_repo: ProductVariantRepoDep
):
    variant = await product_variant_repo.get_by_id(variant_id)
    if not variant or product.id != variant.product_id:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant

CurrentProductVariantDep = Annotated[
    ProductVariation,
    Depends(get_current_product_variant)
]
