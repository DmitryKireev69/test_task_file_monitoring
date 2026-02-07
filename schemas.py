from pydantic import BaseModel
from datetime import datetime


class FileSchema(BaseModel):
    id: int
    path: str
    status: str
    lines: int
    error: str | None
    created_at: datetime
    processed_at: datetime | None
