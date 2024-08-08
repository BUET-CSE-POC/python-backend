import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class FileCreate(BaseModel):
    uploader_id: uuid.UUID
    file_name: str
    file_url: str

class FileUpdate(BaseModel):
    file_name: Optional[str] = None
    status: Optional[str] = None


class File(BaseModel):
    file_id: uuid.UUID
    file_name: str
    uploader_id: uuid.UUID
    file_url: str
    status: str
    uploaded_at: datetime
