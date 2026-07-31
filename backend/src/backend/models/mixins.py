import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, String, DateTime, Enum

from sqlalchemy.orm import Mapped, mapped_column


class LanguageEnum(str, enum.Enum):
    ENGLISH = 'en'
    RUSSIAN = 'ru'
    UZBEK = 'uz'


class IdentityMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())


class SlugMixin:
    slug: Mapped[str] = mapped_column(String(320), unique=True, index=True)


class LanguageMixin:
    lang: Mapped[LanguageEnum] = mapped_column(
        Enum(LanguageEnum, native_enum=False)
    )
