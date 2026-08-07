from typing import Protocol, TypeVar

from backend.models.mixins import LanguageEnum


# Интерфейс
class HasLang(Protocol):
    lang: LanguageEnum


T = TypeVar("T", bound=HasLang)


def resolve_translation(translations: list[T], lang: LanguageEnum, default_lang: LanguageEnum) -> T | None:
    by_lang = {t.lang: t for t in translations}
    return by_lang.get(lang) or by_lang.get(default_lang) or (translations[0] if translations else None)
