from fastapi import APIRouter

from backend.schemas.order import OrderBrief, OrderDetail

router = APIRouter(
    prefix='/orders',
    tags=['order'],
)


@router.post(
    ""
)
async def create_order():
    pass


@router.get(
    '',
    response_model=list[OrderBrief]
)
async def list_my_orders():
    pass


@router.get(
    "/{order_id}",
    response_model=OrderDetail
)
async def get_my_order():
    pass
