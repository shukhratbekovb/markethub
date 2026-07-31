from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import Base
from backend.models.mixins import TimeStampMixin, SlugMixin, LanguageMixin


class Category(TimeStampMixin, Base):
    __tablename__ = 'categories'

    translations: Mapped[list["CategoryTranslation"]] = relationship(
        back_populates="category",
    )

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

