from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File

from backend.dependencies.auth import AdminDep
from backend.dependencies.category import CategoryServiceDep, CurrentCategoryDep
from backend.dependencies.language import LanguageDep
from backend.schemas.category import CategoryRequest, CategoryFilter
from backend.schemas.pagination import PaginationParams

router = APIRouter(
    prefix="/categories",
)


@router.post(
    ""
)
async def create_category(
        service: CategoryServiceDep,
        body: CategoryRequest,
        admin: AdminDep
):
    category = await service.create_category(body)
    return category


@router.get(
    ""
)
async def get_categories(
        service: CategoryServiceDep,
        lang: LanguageDep,
        filters: CategoryFilter = Depends(),
        pagination: PaginationParams = Depends(),
):
    response = await service.list_paginated_categories(filters, pagination, lang)
    return response


@router.get(
    "/all"
)
async def get_all_categories(
        service: CategoryServiceDep,
        lang: LanguageDep,
):
    response = await service.list_categories(lang)
    return response


@router.post(
    "/{category_id}/logo"
)
async def upload_category_logo(
        category_id: UUID,
        category: CurrentCategoryDep,
        service: CategoryServiceDep,
        file: UploadFile = File(...),
):
    await service.upload_category_logo(category, file)


@router.delete(
    "/{category_id}/logo"
)
async def delete_category_logo(
        category_id: UUID,
        category: CurrentCategoryDep,
        service: CategoryServiceDep,
):
    await service.delete_category_logo(category)


@router.get(
    "/{category_id}"
)
async def get_category(
        service: CategoryServiceDep,
        lang: LanguageDep,
        category_id: UUID,
):
    category = await service.get_category(category_id)
    return category


@router.put(
    "/{category_id}"
)
async def update_category(
        service: CategoryServiceDep,
        category_id: UUID,
        body: CategoryRequest,
        category: CurrentCategoryDep
):
    pass


@router.delete(
    "/{category_id}"
)
async def delete_category(
        service: CategoryServiceDep,
        category_id: UUID,
        category: CurrentCategoryDep
):
    await service.delete_category(category)
