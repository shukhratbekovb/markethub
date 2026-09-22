import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File

from backend.dependencies.ownership import get_managed_shop
from backend.dependencies.shop import ShopServiceDep, CurrentShopDep
from backend.schemas.pagination import PaginationParams
from backend.schemas.shop import ShopRequest, ShopResponse

router = APIRouter(
    prefix="/shops",
    tags=["Shop"]
)

OWNER_ID = UUID("143d2f9c-ff76-4bd0-b5d4-fbaa660f239d")


@router.post(
    ""
)
async def create_shop(
        body: ShopRequest,
        service: ShopServiceDep
):
    shop = await service.create_shop(body, owner_id=OWNER_ID)
    return shop


@router.get(
    ""
)
async def get_shops(
        service: ShopServiceDep,
        pagination: PaginationParams = Depends(),
):
    shops = await service.list_paginated_shops(pagination)
    return shops


@router.post(
    "/{shop_id}/logo",
)
async def upload_shop_logo(
        shop_id: UUID,
        shop: CurrentShopDep,
        service: ShopServiceDep,
        file: UploadFile = File(...),
):
    await service.upload_logo(shop, file)


@router.delete(
    "/{shop_id}/logo",
)
async def delete_shop_logo(
        shop_id: UUID,
        shop: CurrentShopDep,
        service: ShopServiceDep,
):
    await service.delete_logo(shop)


@router.get(
    "/{shop_id}",
    response_model=ShopResponse
)
async def get_shop(
        shop_id: UUID,
        service: ShopServiceDep,
):
    shop = await service.get_shop(shop_id)
    return shop


@router.put(
    "/{shop_id}",
    dependencies=[Depends(get_managed_shop)]
)
async def update_shop(
        shop_id: UUID,
        body: ShopRequest,
        service: ShopServiceDep,
        shop: CurrentShopDep
):
    await service.update_shop(shop, body, OWNER_ID)


@router.delete(
    "/{shop_id}",
)
async def delete_shop(
        shop_id: UUID,
        service: ShopServiceDep,
        shop: CurrentShopDep
):
    await service.delete_shop(shop, OWNER_ID)
