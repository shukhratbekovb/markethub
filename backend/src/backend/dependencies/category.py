from uuid import UUID

from fastapi import Depends, HTTPException
from typing import Annotated

from backend.dependencies.database import SessionDep
from backend.dependencies.language import LanguageDep
from backend.models import Category
from backend.repository.category import CategoryRepository
from backend.services.category import CategoryService


async def get_category_repo(
        session: SessionDep
) -> CategoryRepository:
    return CategoryRepository(session)


CategoryRepoDep = Annotated[
    CategoryRepository,
    Depends(get_category_repo)
]


async def get_category_service(
        session: SessionDep,
        category_repo: CategoryRepoDep
) -> CategoryService:
    return CategoryService(session, category_repo)


CategoryServiceDep = Annotated[
    CategoryService,
    Depends(get_category_service)
]


async def get_current_category(
        category_id: UUID,
        repo: CategoryRepoDep
) -> Category:
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


CurrentCategoryDep = Annotated[
    Category,
    Depends(get_current_category)
]
