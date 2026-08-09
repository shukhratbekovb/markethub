from uuid import UUID

from pydantic import BaseModel, Field

from backend.schemas.mixins import TimeActionSchemaMixin


class ShopRequest(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=320,
    )


class ShopBrief(BaseModel):
    id: UUID
    name: str
    is_active: bool
    owner_id: UUID

class ShopResponse(TimeActionSchemaMixin, ShopBrief):
    pass
    # products: list