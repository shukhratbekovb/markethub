from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.file_storage import save_upload, delete_file
from backend.core.i18n import resolve_translation
from backend.models import Category, CategoryTranslation
from backend.models.mixins import LanguageEnum
from backend.repository.category import CategoryRepository
from backend.schemas.category import CategoryRequest, CategoryResponse, CategoryBrief, CategoryFilter
from backend.schemas.pagination import PaginationParams, Page


class CategoryService:
    def __init__(
            self,
            session: AsyncSession,
            category_repo: CategoryRepository
    ):
        self.session = session
        self.category_repo = category_repo

    async def create_category(
            self,
            body: CategoryRequest
    ) -> Category:
        category = Category(
            translations=[
                CategoryTranslation(
                    **t.model_dump()
                )
                for t in body.translations
            ]
        )
        category = await self.category_repo.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def update_category(
            self,
            category: Category,
            body: CategoryRequest
    ):
        pass

    async def delete_category(
            self,
            category: Category
    ) -> None:
        await self.category_repo.delete(category)
        await self.session.commit()

    async def get_category(
            self,
            category_id: UUID,
            lang: LanguageEnum = LanguageEnum.RUSSIAN
    ) -> CategoryResponse:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        translation = resolve_translation(
            translations=category.translations,
            lang=lang,
            default_lang=LanguageEnum.RUSSIAN
        )
        if not translation:
            raise HTTPException(status_code=404, detail="Category not found")

        return CategoryResponse(
            id=category.id,
            name=translation.name,
            slug=translation.slug,
            created_at=category.created_at,
            updated_at=category.updated_at,
            # products
        )

    async def list_categories(
            self,
            lang: LanguageEnum = LanguageEnum.RUSSIAN
    ) -> list[CategoryBrief]:
        categories = await self.category_repo.list_all()

        response: list[CategoryBrief] = []

        for category in categories:
            translation = resolve_translation(
                translations=category.translations,
                lang=lang,
                default_lang=LanguageEnum.RUSSIAN
            )
            if not translation:
                continue
            response.append(
                CategoryBrief(
                    id=category.id,
                    name=translation.name,
                    slug=translation.slug,
                    created_at=category.created_at,
                    updated_at=category.updated_at,
                )
            )
        return response

    async def list_paginated_categories(
            self,
            filters: CategoryFilter,
            pagination: PaginationParams,
            lang: LanguageEnum = LanguageEnum.RUSSIAN
    ):
        categories = await self.category_repo.list_paginated(
            filters=filters,
            pagination=pagination,
        )
        response = Page(
            items=[],
            total=categories.total,
            page=categories.page,
            size=categories.size,
            pages=categories.pages,
            has_next=categories.has_next,
            has_prev=categories.has_prev
        )
        for category in categories.items:
            translation = resolve_translation(
                translations=category.translations,
                lang=lang,
                default_lang=LanguageEnum.RUSSIAN
            )
            if not translation:
                continue
            response.items.append(
                CategoryBrief(
                    id=category.id,
                    name=translation.name,
                    slug=translation.slug,
                    created_at=category.created_at,
                    updated_at=category.updated_at,
                )
            )
        return response

    async def upload_category_logo(
            self,
            category: Category,
            file: UploadFile
    ):
        old_logo = category.logo_path
        category.logo_path = await save_upload("categories", category.id, file)
        await self.category_repo.update(category)

        if old_logo:
            delete_file(old_logo)

        await self.session.commit()

    async def delete_category_logo(
            self,
            category: Category
    ):
        if category.logo_path:
            delete_file(category.logo_path)
            category.logo_path = None
            await self.category_repo.update(category)
            await self.session.commit()
