import uuid
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.dependencies.shop import ShopServiceDep, CurrentShopDep
from backend.schemas.pagination import PaginationParams
from backend.schemas.shop import ShopRequest

router = APIRouter(
    prefix="/shops",
    tags=["Shop"]
)

OWNER_ID = uuid.uuid4()


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


@router.get(
    "/{shop_id}",
)
async def get_shop(
        shop_id: UUID,
        service: ShopServiceDep,
):
    shop = await service.get_shop(shop_id)
    return shop


@router.put(
    "/{shop_id}",
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
