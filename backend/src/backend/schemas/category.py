from enum import Enum
from uuid import UUID

from fastapi import Query
from pydantic import Field, BaseModel, field_validator
from pydantic.dataclasses import dataclass
from sqlalchemy import Select, select

from backend.models import CategoryTranslation, Category
from backend.schemas.filters import BaseFilter
from backend.schemas.mixins import TimeActionSchemaMixin
from backend.schemas.translation import TranslationSchema, LANGUAGES


class CategorySortEnum(str, Enum):
    NAME_ASC = "name:asc"
    NAME_DESC = "name:desc"
    CREATED_AT_ASC = "created_at:asc"
    CREATED_AT_DESC = "created_at:desc"


_SORT_COLUMNS = {
    CategorySortEnum.NAME_ASC: CategoryTranslation.name.asc(),
    CategorySortEnum.NAME_DESC: CategoryTranslation.name.desc(),
    CategorySortEnum.CREATED_AT_ASC: Category.created_at.asc(),
    CategorySortEnum.CREATED_AT_DESC: Category.created_at.desc(),
}


@dataclass(frozen=True)
class CategoryFilter(BaseFilter):
    q: str | None = Query(
        default=None
    )
    sort_column: CategorySortEnum = Query(
        default=CategorySortEnum.CREATED_AT_DESC, alias="sort"
    )

    def filter(self, stmt: Select) -> Select:
        if self.q:
            stmt = stmt.where(
                Category.translations.any(
                    CategoryTranslation.name.ilike(f"%{self.q}%")
                )
            )
        return stmt

    def sort(self, stmt: Select) -> Select:
        sort_column = _SORT_COLUMNS.get(self.sort_column)

        if self.sort_column in {
            CategorySortEnum.NAME_ASC,
            CategorySortEnum.NAME_DESC,
        }:
            # Вместо прямого join, который размножает строки,
            # мы коррелируем подзапрос для упорядочивания.
            # Это полностью исключает появление дубликатов на уровне SQL.
            subq = (
                select(CategoryTranslation.name)
                .where(CategoryTranslation.category_id == Category.id)
                # Берем первый попавшийся перевод для сортировки, если язык не передан,
                # либо сортируем по алфавиту внутри категории
                .limit(1)
                .correlate(Category)
            ).scalar_subquery()

            # В зависимости от ASC/DESC применяем направление к подзапросу
            if self.sort_column == CategorySortEnum.NAME_ASC:
                return stmt.order_by(subq.asc())
            else:
                return stmt.order_by(subq.desc())

        return stmt.order_by(sort_column)


class CategoryTranslationSchema(TranslationSchema):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)


class CategoryRequest(BaseModel):
    translations: list[CategoryTranslationSchema]

    @field_validator("translations", mode="after")
    @classmethod
    def validate_translations(cls, v: list[CategoryTranslationSchema]):
        languages = [t.lang for t in v]
        if frozenset(languages) != LANGUAGES:
            raise ValueError("Не указан один из языков")
        return v


class CategoryBrief(TimeActionSchemaMixin):
    id: UUID
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)
    logo_url: str | None = None


class CategoryResponse(CategoryBrief):
    # products
    pass
