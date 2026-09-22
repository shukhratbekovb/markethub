from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from fastapi import Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import Select

from backend.models.order import OrderStatus, Order
from backend.schemas.filters import BaseFilter


class OrderSortEnum(str, Enum):
    CREATED_AT_ASC = "created_at:asc"
    CREATED_AT_DESC = "created_at:desc"


_SORT_COLUMNS = {
    OrderSortEnum.CREATED_AT_ASC: Order.created_at.asc(),
    OrderSortEnum.CREATED_AT_DESC: Order.created_at.desc(),
}


@dataclass(frozen=True)
class OrderFilter(BaseFilter):
    status: OrderStatus | None = None
    created_at_from: datetime | None = None  # 2026-01-01
    created_at_to: datetime | None = None  # 2025-01-01
    sort_column: OrderSortEnum | None = Query(
        default=OrderSortEnum.CREATED_AT_DESC,
        alias="sort",
    )

    def __post_init__(self):
        if self.created_at_from is not None and self.created_at_to is not None:
            if self.created_at_from > self.created_at_to:
                raise HTTPException(
                    status_code=400,
                    detail="created_at_from must be <= created_at_to",
                )

    def filter(
            self,
            stmt: Select,
    ) -> Select:
        if self.status is not None:
            stmt = stmt.where(
                Order.status == self.status,
            )
        if self.created_at_from is not None:
            stmt = stmt.where(
                Order.created_at >= self.created_at_from,
            )
        if self.created_at_to is not None:
            stmt = stmt.where(
                Order.created_at <= self.created_at_to,
            )
        return stmt

    def sort(
            self,
            stmt: Select
    ) -> Select:
        sort_column = _SORT_COLUMNS.get(self.sort_column)
        return stmt.order_by(sort_column) if sort_column is not None else stmt


class OrderBrief(BaseModel):
    id: UUID
    user_id: UUID
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime

class OrderItemResponse(BaseModel):
    id: UUID
    variant_id: UUID
    product_name_snapshot: str
    variant_label_snapshot: str | None = None
    unit_price: Decimal
    quantity: int

class OrderDetail(OrderBrief):
    items: list[OrderItemResponse]
