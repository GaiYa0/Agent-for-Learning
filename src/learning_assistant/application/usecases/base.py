"""Abstract base for all use cases."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from learning_assistant.application.dto.common import Result

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class BaseUseCase(ABC, Generic[TInput, TOutput]):
    """Common interface every use case must implement."""

    @abstractmethod
    async def execute(self, input_dto: TInput) -> Result[TOutput]:
        ...
