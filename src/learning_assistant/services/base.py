"""Abstract base for all services."""

from abc import ABC, abstractmethod


class BaseService(ABC):
    """Common interface every service must implement."""

    @property
    @abstractmethod
    def service_name(self) -> str:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...
