"""Shared base model configuration for all domain models."""

from pydantic import BaseModel, ConfigDict


class DomainModel(BaseModel):
    """Base for all domain models with strict validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
    )
