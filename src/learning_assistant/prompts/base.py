"""Abstract base for all prompt templates."""

from abc import ABC, abstractmethod


class BasePromptTemplate(ABC):
    """Common interface every prompt template must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        ...

    @property
    @abstractmethod
    def required_variables(self) -> set[str]:
        ...

    @abstractmethod
    def build(self, **kwargs: str) -> str:
        """Build the final prompt string from variables."""
        ...

    def validate(self, **kwargs: str) -> None:
        """Check that all required variables are present."""
        from learning_assistant.prompts.exceptions import ValidationError

        missing = self.required_variables - set(kwargs.keys())
        if missing:
            raise ValidationError(f"Missing required variables: {missing}")

    def render(self, **kwargs: str) -> str:
        """Validate then build."""
        self.validate(**kwargs)
        return self.build(**kwargs)
