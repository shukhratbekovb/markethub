from fastapi import APIRouter
from starlette import status

from backend.dependencies.auth import AuthServiceDep, CurrentUserDep
from backend.schemas.auth import LoginOutSchema, LoginSchema, RegisterCustomer, RegisterSeller, RefreshToken, \
    ChangePasswordSchema

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register-customer")
async def register_customer(
        body: RegisterCustomer,
        service: AuthServiceDep
):
    user = await service.register_customer(body)
    return user


@router.post("/register-seller")
async def register_seller(
        body: RegisterSeller,
        service: AuthServiceDep
):
    user = await service.register_seller(body)
    return user


@router.post(
    "/login",
    response_model=LoginOutSchema, )
async def login_user(
        body: LoginSchema,
        service: AuthServiceDep
):
    token =  await service.login_user(body)
    return token


@router.post(
    "/refresh",
    response_model=LoginOutSchema,
)
async def refresh_token(
        body: RefreshToken,
        service: AuthServiceDep
):
    token = await service.refresh_token(body)
    return token



@router.post("/change-password",status_code=status.HTTP_200_OK)
async def change_password(
        body: ChangePasswordSchema,
        current_user: CurrentUserDep,
        service: AuthServiceDep
):
    await service.change_password(current_user, body)

