"""Pagination schemas, common to all repositories."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class PaginationParams(BaseModel):
    """Page/size requested by a client.

    Attributes:
        page: Page number, starting at 1.
        size: Rows per page, between 5 and 200.
    """

    page: int = Field(ge=1, default=1)
    size: int = Field(ge=5, le=200, default=100)

    @property
    def limit(self) -> int:
        """SQL `LIMIT` value for this page."""
        return self.size

    @property
    def offset(self) -> int:
        """SQL `OFFSET` value for this page."""
        return (self.page - 1) * self.size


@dataclass
class Page(Generic[T]):
    """One page of results plus pagination metadata."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(
            cls,
            items: list[T],
            total: int,
            params: PaginationParams
    ) -> "Page[T]":
        """Build a `Page` from a slice of `items` and the total row count.

        Args:
            items: Rows for the requested page.
            total: Total number of matching rows across all pages.
            params: The pagination request this page answers.

        Returns:
            A populated `Page`, with `pages`/`has_next`/`has_prev`
            derived from `total` and `params`.
        """
        pages = (total + params.size - 1) // params.size

        return cls(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            pages=pages,
            has_next=params.page < pages,
            has_prev=params.page > 1,
        )
