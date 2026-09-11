from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import generate_username, hash_password, verify_password, create_access_token, \
    create_refresh_token, decode_token
from backend.models import User, Shop
from backend.models.user import UserRole
from backend.repository.shop import ShopRepository
from backend.repository.user import UserRepository
from backend.schemas.auth import RegisterCustomer, RegisterSeller, RegisterUser, LoginSchema, LoginOutSchema, \
    RefreshToken, ChangePasswordSchema


class AuthService:
    def __init__(
            self,
            session: AsyncSession,
            user_repo: UserRepository,
            shop_repo: ShopRepository
    ):
        self.session = session
        self.user_repo = user_repo
        self.shop_repo = shop_repo

    async def _register_user(
            self,
            body: RegisterUser,
            role: UserRole = UserRole.CUSTOMER
    ) -> User:
        username = await generate_username(
            self.session,
            body.first_name,
            body.last_name,
        )
        hashed_password = hash_password(body.password)
        exist_user = await self.user_repo.get_by_email(body.email)
        if exist_user is not None:
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            )
        user = User(
            username=username,
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone=body.phone,
            hashed_password=hashed_password,
            role=role
        )

        user = await self.user_repo.add(user)
        return user

    async def register_customer(
            self,
            body: RegisterCustomer
    ) -> User:
        user = await self._register_user(body)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def register_seller(
            self,
            body: RegisterSeller
    ) -> User:
        user = await self._register_user(body, UserRole.SELLER)

        shop = Shop(
            name=body.shop.name,
            owner_id=user.id
        )
        await self.shop_repo.add(shop)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def login_user(
            self,
            body: LoginSchema
    ):
        user = await self.user_repo.get_by_username(body.username)

        if user is None or not verify_password(body.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid Credentials",
            )

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return LoginOutSchema(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_token(
            self,
            body: RefreshToken
    ):
        user_id = decode_token(body.refresh_token, "refresh")
        user = await self.user_repo.get_by_id(user_id)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="Inactive user",
            )

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return LoginOutSchema(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def change_password(
            self,
            user: User,
            body: ChangePasswordSchema
    ):
        if not verify_password(body.new_password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid Credentials",
            )
        hashed_password = hash_password(body.new_password)
        user.hashed_password = hashed_password
        await self.user_repo.update(user)
        await self.session.commit()
