from fastapi import APIRouter

from backend.api.v1.category import router as category_router
from backend.api.v1.shop import router as shop_router

v1_router = APIRouter(
    prefix="/api/v1",
)

v1_router.include_router(
    category_router
)
v1_router.include_router(
    shop_router
)
