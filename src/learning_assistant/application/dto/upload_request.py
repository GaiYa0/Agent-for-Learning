"""Upload request DTO."""

from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    file_path: str = Field(min_length=1)
    source: str = ""


class IndexResult(BaseModel):
    filename: str
    chunks_indexed: int = Field(ge=0)
    document_id: str = ""
