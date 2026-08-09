from uuid import UUID

from backend.core.file_storage import save_upload, delete_file
from backend.models.mixins import LanguageEnum
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.models import Shop
from backend.repository.shop import ShopRepository
from backend.schemas.pagination import PaginationParams
from backend.schemas.shop import ShopRequest


class ShopService:
    def __init__(
            self,
            session: AsyncSession,
            shop_repo: ShopRepository,
    ):
        self.session = session
        self.shop_repo = shop_repo

    async def create_shop(
            self,
            body: ShopRequest,
            owner_id: UUID
    ) -> Shop:
        shop = Shop(
            name=body.name,
            owner_id=owner_id
        )
        await self.shop_repo.add(shop)
        await self.session.commit()
        await self.session.refresh(shop)
        return shop

    async def update_shop(
            self,
            shop: Shop,
            body: ShopRequest,
            current_user_id: UUID
    ) -> None:
        if shop.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update a shop owned by the current user"
            )
        shop.name = body.name
        await self.shop_repo.update(shop)
        await self.session.commit()

    async def delete_shop(
            self,
            shop: Shop,
            current_user_id: UUID
    ) -> None:
        if shop.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update a shop owned by the current user"
            )
        await self.shop_repo.delete(shop)
        await self.session.commit()

    async def get_shop(
            self,
            shop_id: UUID
    ) -> Shop:
        shop = await self.shop_repo.get_by_id(shop_id)
        if not shop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shop not found"
            )
        return shop

    async def list_paginated_shops(
            self,
            pagination: PaginationParams
    ):
        shops = await self.shop_repo.list_paginated(pagination)
        return shops

    async def upload_logo(
            self,
            shop: Shop,
            file: UploadFile
    ):
        old_logo = shop.logo_path
        shop.logo_path = await save_upload("shops", shop.id, file)
        await self.shop_repo.update(shop)

        if old_logo:
            delete_file(old_logo)

        await self.session.commit()

    async def delete_logo(
            self,
            shop: Shop,
    ):
        if shop.logo_path:
            delete_file(shop.logo_path)
            shop.logo_path = None
            await self.shop_repo.update(shop)
            await self.session.commit()
