"""Base filter/sort abstraction for repository queries."""

from abc import ABC, abstractmethod

from sqlalchemy import Select


class BaseFilter(ABC):
    """Encapsulates filtering and sorting on top of a repository's `base_query`."""

    @abstractmethod
    def filter(
            self,
            stmt: Select,
    ) -> Select:
        """Apply `WHERE` conditions to `stmt`.

        Args:
            stmt: The base query to filter.

        Returns:
            `stmt` with filter conditions applied.
        """
        pass

    @abstractmethod
    def sort(
            self,
            stmt: Select
    ) -> Select:
        """Apply `ORDER BY` to `stmt`.

        Args:
            stmt: The base query to sort.

        Returns:
            `stmt` with ordering applied.
        """
        pass
