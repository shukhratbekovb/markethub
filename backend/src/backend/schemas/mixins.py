from datetime import datetime

from pydantic import BaseModel


class TimeActionSchemaMixin(BaseModel):
    created_at: datetime
    updated_at: datetime