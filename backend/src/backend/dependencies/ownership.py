from uuid import UUID

from fastapi import HTTPException

from backend.dependencies.auth import StaffDep
from backend.dependencies.shop import ShopRepoDep
from backend.models.user import UserRole


async def get_managed_shop(
        shop_id: UUID,
        user: StaffDep,
        shop_repo: ShopRepoDep
):
    shop = await shop_repo.get_by_id(shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    if user.role == UserRole.ADMIN or shop.owner_id == user.id:
        return
    raise HTTPException(status_code=403, detail="Not enough permissions")