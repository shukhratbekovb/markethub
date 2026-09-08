from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, computed_field, Field


class CartItemResponse(BaseModel):
    variant_id: UUID
    sku: str
    quantity: int
    unit_price: Decimal

    @computed_field
    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


class CartResponse(BaseModel):
    items: list[CartItemResponse]

    @computed_field
    @property
    def total(self) -> Decimal:
        return sum((item.subtotal for item in self.items), Decimal("0"))


class CartItemAddRequest(BaseModel):
    variant_id: UUID
    quantity: int = Field(ge=1)


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(ge=1)
