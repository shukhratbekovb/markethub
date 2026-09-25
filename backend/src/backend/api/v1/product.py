from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from backend.dependencies.auth import StaffDep
from backend.dependencies.language import LanguageDep
from backend.dependencies.product import ProductServiceDep, CurrentProductDep, CurrentProductVariantDep
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.product import ProductCreateResponse, ProductCreate, ProductResponse, ProductBrief, ProductUpdate, \
    ProductFilter, ProductVariantCreate, StockAdjustRequest, StockSetRequest

router = APIRouter(
    prefix="/products",
    tags=["product"],
    dependencies=StaffDep
)


@router.patch(
    "/{product_id}/variants/{variant_id}/adjust-stock",
)
async def adjust_stock(
        staff: StaffDep,
        product_id: UUID,
        variant_id: UUID,
        variant: CurrentProductVariantDep,
        body: StockAdjustRequest,
        service: ProductServiceDep,
):
    await service.adjust_stock(variant, body)


@router.patch(
    "/{product_id}/variants/{variant_id}/set-stock",
)
async def set_stock(
        staff: StaffDep,
        product_id: UUID,
        variant_id: UUID,
        variant: CurrentProductVariantDep,
        body: StockSetRequest,
        service: ProductServiceDep,

):
    await service.set_stock(variant, body)


@router.post(
    "/{product_id}/variants",
    status_code=status.HTTP_201_CREATED,
)
async def create_product_variant(
        staff: StaffDep,
        product_id: UUID,
        product: CurrentProductDep,
        service: ProductServiceDep,
        body: ProductVariantCreate
):
    await service.add_variant(product, body)


@router.get(
    "/{product_id}/variants",
)
async def list_product_variants(
        staff: StaffDep,
        product_id: UUID,
):
    pass


@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
async def get_product(
        product_id: UUID,
        service: ProductServiceDep,
        lang: LanguageDep
):
    response = await service.get_product(product_id, lang)
    return response


@router.put(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_product(
        staff: StaffDep,
        product_id: UUID,
        product: CurrentProductDep,
        service: ProductServiceDep,
        body: ProductUpdate,
):
    await service.update_product(product, body)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
        staff: StaffDep,
        product_id: UUID,
        product: CurrentProductDep,
        service: ProductServiceDep
):
    await service.delete_product(product)


@router.get(
    "",
    response_model=Page[ProductBrief]
)
async def get_products(
        service: ProductServiceDep,
        lang: LanguageDep,
        pagination: PaginationParams = Depends(),
        filters: ProductFilter = Depends()
):
    response = await service.list_paginated_products(
        pagination=pagination,
        lang=lang,
        filters=filters
    )
    return response


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductCreateResponse
)
async def create_product(
        staff: StaffDep,
        body: ProductCreate,
        service: ProductServiceDep
):
    response = await service.create_product(body)
    return response
