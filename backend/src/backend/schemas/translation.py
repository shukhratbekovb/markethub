from pydantic import BaseModel

from backend.models.mixins import LanguageEnum

# ru en uz
LANGUAGES = frozenset(language.value for language in LanguageEnum)

class TranslationSchema(BaseModel):
    lang: LanguageEnum

