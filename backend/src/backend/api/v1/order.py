from fastapi import APIRouter

from backend.dependencies.auth import CustomerDep
from backend.schemas.order import OrderBrief, OrderDetail

router = APIRouter(
    prefix='/orders',
    tags=['order'],
)


@router.post(
    ""
)
async def create_order(
        customer: CustomerDep
):
    pass


@router.get(
    '',
    response_model=list[OrderBrief]
)
async def list_my_orders(
        customer: CustomerDep
):
    pass


@router.get(
    "/{order_id}",
    response_model=OrderDetail
)
async def get_my_order(
        customer: CustomerDep
):
    pass
