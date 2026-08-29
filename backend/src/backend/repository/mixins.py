"""Composable async repository mixins — CRUD and listing, kept separate."""

from typing import TypeVar, Generic
from uuid import UUID

from sqlalchemy import Select, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from backend.core.enums import LanguageEnum
from backend.schemas.filters import BaseFilter
from backend.schemas.pagination import Page, PaginationParams

T = TypeVar("T", bound=DeclarativeBase)


class RepositoryMixin(Generic[T]):
    """Base contract shared by every repository mixin.

    A concrete repository must provide `model` and `session` — the
    other mixins rely on them.
    """

    model: type[T]
    session: AsyncSession


class AddRepositoryMixin(RepositoryMixin[T]):
    """Adds `add()` — insert a new row."""

    async def add(self, obj: T) -> T:
        """Add `obj` to the session and flush it.

        Args:
            obj: A new (transient) model instance to persist.

        Returns:
            The same instance, now attached to the session.
        """
        self.session.add(obj)
        await self.session.flush()
        return obj


class RetrieveRepositoryMixin(RepositoryMixin[T]):
    """Adds `get_by_id()` — fetch a single row by primary key."""

    base_query: Select

    async def get_by_id(self, obj_id: int | UUID) -> T | None:
        """Find a single row by primary key.

        Args:
            obj_id: Primary key value to look up.

        Returns:
            The matching instance, or `None` if no row matches.
        """
        stmt = self.base_query.where(self.model.id == obj_id)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        return obj


class UpdateRepositoryMixin(RepositoryMixin[T]):
    """Adds `update()` — merge changes into a tracked row."""

    async def update(self, obj: T) -> T:
        """Merge `obj`'s state into the session and flush it.

        Args:
            obj: A (possibly detached) instance carrying the new state.

        Returns:
            The session-tracked instance returned by `session.merge()` —
            not necessarily the same object that was passed in as `obj`.
        """
        merged = await self.session.merge(obj)
        await self.session.flush()
        return merged


class DeleteRepositoryMixin(RepositoryMixin[T]):
    """Adds `delete()` — remove a row."""

    async def delete(self, obj: T) -> None:
        """Delete `obj` and flush the change.

        Args:
            obj: The instance to remove.
        """
        await self.session.delete(obj)
        await self.session.flush()


class ListRepositoryMixin(RepositoryMixin[T]):
    """Adds `list_all()` — unpaginated listing.

    For entities with a small, bounded row count per tenant (Pipeline,
    Stage, Role, Team, custom_field_definition). For potentially large
    entities, use `PaginatedListRepositoryMixin` instead.
    """

    base_query: Select

    async def list_all(
            self,
            filters: BaseFilter | None = None,
    ) -> list[T]:
        """Return every row matching `filters`, with no pagination.

        Args:
            filters: Optional filter/sort to apply on top of `base_query`.

        Returns:
            All matching rows.
        """
        stmt = self.base_query

        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        objs = result.scalars().all()
        return list(objs)


class PaginatedListRepositoryMixin(RepositoryMixin[T]):
    """Adds `list_paginated()` — listing with pagination and a total count."""

    base_query: Select

    async def list_paginated(
            self,
            pagination: PaginationParams,
            filters: BaseFilter | None = None,
            lang: LanguageEnum = LanguageEnum.RUSSIAN,
    ) -> Page[T]:
        """Return one page of rows matching `filters`.

        Args:
            pagination: Requested page/size.
            filters: Optional filter/sort — also applied before the
                count, so `total` reflects the filtered set, not the
                whole table.

        Returns:
            A `Page` with `items`, `total`, and pagination metadata.
        """
        stmt = self.base_query

        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(stmt)
        objs = result.scalars().all()

        return Page.create(items=list(objs), total=total, params=pagination)
