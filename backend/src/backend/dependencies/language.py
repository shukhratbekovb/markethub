from typing import Annotated

from fastapi import Depends, Header

from backend.core.configs import settings
from backend.models.mixins import LanguageEnum


async def get_language(accept_language: str | None = Header(default=None)) -> LanguageEnum:
    if accept_language:
        # ru-RU,uz-UZ
        primary_tag = accept_language.split(",")[0].split("-")[0].strip().lower()
        try:
            return LanguageEnum(primary_tag)
        except ValueError:
            pass
    return settings.default_language


LanguageDep = Annotated[LanguageEnum, Depends(get_language)]