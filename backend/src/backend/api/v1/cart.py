from fastapi import APIRouter
from sqlalchemy import UUID

from backend.dependencies.cart import CartServiceDep
from backend.schemas.cart import CartItemAddRequest, CartItemUpdateRequest

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
)

OWNER_ID = UUID("143d2f9c-ff76-4bd0-b5d4-fbaa660f239d")


@router.get("/")
async def get_cart(
        service: CartServiceDep
):
    cart = await service.get_cart(OWNER_ID)
    return cart


@router.post("/items")
async def add_item(
        body: CartItemAddRequest,
        service: CartServiceDep,
):
    await service.add_item(
        user_id=OWNER_ID,
        variant_id=body.variant_id,
        quantity=body.quantity,
    )


@router.patch("/items/{variant_id}")
async def update_item(
        variant_id: UUID,
        body: CartItemUpdateRequest,
        service: CartServiceDep,
):
    await service.update_item(
        user_id=OWNER_ID,
        variant_id=variant_id,
        quantity=body.quantity,
    )


@router.delete("/items/{variant_id}")
async def remove_item(
        variant_id: UUID,
        service: CartServiceDep,
):
    await service.remove_item(
        user_id=OWNER_ID,
        variant_id=variant_id,
    )


@router.delete("/")
async def clear_cart(
        service: CartServiceDep,
):
    await service.clear_cart(
        user_id=OWNER_ID,
    )
