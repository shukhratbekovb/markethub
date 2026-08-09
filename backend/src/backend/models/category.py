from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.configs import settings
from backend.models import Base
from backend.models.mixins import TimeStampMixin, SlugMixin, LanguageMixin


class Category(TimeStampMixin, Base):
    __tablename__ = 'categories'

    logo_path: Mapped[str | None] = mapped_column(
        String(500)
    )

    translations: Mapped[list["CategoryTranslation"]] = relationship(
        back_populates="category",
    )

    @hybrid_property
    def logo_url(self):
        if self.logo_path is None:
            return None
        return f"{settings.upload_root}/{self.logo_path}"


class CategoryTranslation(LanguageMixin, SlugMixin, Base):
    __tablename__ = 'category_translations'

    name: Mapped[str] = mapped_column(
        String(255)
    )
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )

    category: Mapped[Category] = relationship(
        back_populates="translations",
    )
