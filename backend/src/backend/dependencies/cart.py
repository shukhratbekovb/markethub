from typing import Annotated

from fastapi import Depends

from backend.dependencies.database import SessionDep
from backend.dependencies.product import ProductVariantRepoDep
from backend.repository.cart import CartRepository, CartItemRepository
from backend.services.cart import CartService


async def get_cart_repo(
        session: SessionDep
) -> CartRepository:
    return CartRepository(session)


CartRepoDep = Annotated[
    CartRepository,
    Depends(get_cart_repo)
]


async def get_care_item_repo(
        session: SessionDep
) -> CartItemRepository:
    return CartItemRepository(session)


CartItemRepoDep = Annotated[
    CartItemRepository,
    Depends(get_care_item_repo)
]


async def get_cart_service(
        session: SessionDep,
        cart_repo: CartRepoDep,
        cart_item_repo: CartItemRepoDep,
        variant_repo: ProductVariantRepoDep
) -> CartService:
    return CartService(
        session=session,
        cart_repo=cart_repo,
        cart_item_repo=cart_item_repo,
        variant_repo=variant_repo
    )


CartServiceDep = Annotated[
    CartService,
    Depends(get_cart_service)
]
