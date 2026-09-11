import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.core.security import password_schema
from backend.schemas.shop import ShopRequest


class LoginSchema(BaseModel):
    username: str
    password: str


class LoginOutSchema(BaseModel):
    access_token: str  # JWT
    refresh_token: str  # JWT


class RegisterUser(BaseModel):
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    email: EmailStr
    password: str
    phone: str | None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str):
        if not password_schema.validate(v):
            raise ValueError("Invalid password")
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str | None:
        if v is None:
            return v
        try:
            parsed = phonenumbers.parse(v)
            is_valid = phonenumbers.is_valid_number(parsed)
            if not is_valid:
                raise NumberParseException('Invalid phone number')
        except NumberParseException:
            raise ValueError("Invalid phone number")

        return f"+{parsed.country_code} {parsed.national_number}"


class RegisterCustomer(RegisterUser):
    pass


class RegisterSeller(RegisterUser):
    shop: ShopRequest


class RefreshToken(BaseModel):
    refresh_token: str


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str):
        if not password_schema.validate(v):
            raise ValueError("Invalid password")
        return v
