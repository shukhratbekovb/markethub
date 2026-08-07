from fastapi import APIRouter, Depends

from backend.dependencies.category import CategoryServiceDep
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
        body: CategoryRequest
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
