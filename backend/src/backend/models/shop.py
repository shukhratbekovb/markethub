from uuid import UUID

from backend.core.configs import settings
from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import Base
from backend.models.mixins import TimeStampMixin


class Shop(TimeStampMixin, Base):
    __tablename__ = 'shops'

    owner_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('users.id', ondelete="SET NULL"),
    )
    name: Mapped[str] = mapped_column(
        String(320)
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    logo_path: Mapped[str | None] = mapped_column(
        String(500)
    )

    owner: Mapped["User"] = relationship(
        back_populates="shops"
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="shop"
    )

    @hybrid_property
    def logo_url(self):
        if self.logo_path is None:
            return None
        return f"{settings.upload_root}/{self.logo_path}"