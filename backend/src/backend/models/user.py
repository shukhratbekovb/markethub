import enum

from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import Base
from backend.models.mixins import TimeStampMixin

class UserRole(str, enum.Enum):
    CUSTOMER = 'customer'
    SELLER = 'seller'
    ADMIN = 'admin'



class User(TimeStampMixin, Base):
    __tablename__ = 'users'

    first_name: Mapped[str] = mapped_column(
        String(255)
    )
    last_name: Mapped[str] = mapped_column(
        String(255)
    )
    email: Mapped[str] = mapped_column(
        String(320), unique=True, index=True
    )
    username: Mapped[str] = mapped_column(
        String(320), unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255)
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False), default=UserRole.CUSTOMER
    ) # VARCHAR
    phone: Mapped[str | None] = mapped_column(
        String(20)
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )

    shops: Mapped[list["Shop"]] = relationship(
        back_populates="owner"
    )
