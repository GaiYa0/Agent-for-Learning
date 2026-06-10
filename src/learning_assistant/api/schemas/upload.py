"""Upload API schemas."""

from pydantic import BaseModel, Field


class UploadResponseDTO(BaseModel):
    filename: str
    chunks_indexed: int = Field(ge=0)
    document_id: str = ""
