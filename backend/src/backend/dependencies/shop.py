from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from backend.dependencies.database import SessionDep
from backend.models import Shop
from backend.repository.shop import ShopRepository
from backend.services.shop import ShopService


async def get_shop_repo(
        session: SessionDep
) -> ShopRepository:
    return ShopRepository(session)


ShopRepoDep = Annotated[
    ShopRepository,
    Depends(get_shop_repo),
]


async def get_shop_service(
        session: SessionDep,
        shop_repo: ShopRepoDep
) -> ShopService:
    return ShopService(session, shop_repo)


ShopServiceDep = Annotated[
    ShopService,
    Depends(get_shop_service),
]


async def get_current_shop(
        shop_id: UUID,
        repo: ShopRepoDep
) -> Shop:
    shop = await repo.get_by_id(shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


CurrentShopDep = Annotated[
    Shop,
    Depends(get_current_shop),
]
