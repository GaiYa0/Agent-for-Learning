"""Web search tool — wraps SearchService."""

from learning_assistant.models.tool import ToolResult
from learning_assistant.services.factory import ServiceFactory
from learning_assistant.services.search.search_service import SearchService
from learning_assistant.tools.base import BaseTool, ParameterSpec
from learning_assistant.tools.exceptions import ToolExecutionError, ToolValidationError


class SearchTool(BaseTool):
    """Searches the web for information."""

    def __init__(self, search_service: SearchService | None = None) -> None:
        self._search_service = search_service or ServiceFactory().create_search_service()

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for information on a given topic"

    @property
    def category(self) -> str:
        return "search"

    @property
    def parameters(self) -> dict[str, ParameterSpec]:
        return {
            "query": ParameterSpec(
                type="string",
                description="The search query",
                required=True,
            ),
            "max_results": ParameterSpec(
                type="integer",
                description="Maximum number of results to return",
                required=False,
            ),
        }

    async def execute(self, **kwargs: str) -> ToolResult:
        query = kwargs["query"]
        raw_max = kwargs.get("max_results", "5")
        try:
            max_results = int(raw_max)
        except ValueError as e:
            raise ToolValidationError(
                f"max_results must be an integer, got '{raw_max}'"
            ) from e
        if max_results < 1:
            raise ToolValidationError("max_results must be >= 1")
        try:
            response = await self._search_service.search(
                query, max_results=max_results
            )
        except Exception as e:
            raise ToolExecutionError(f"Search failed: {e}") from e
        lines = [
            f"[{r.title}]({r.url}): {r.snippet}" for r in response.results
        ]
        return ToolResult(
            tool_call_id="",
            success=True,
            content="\n".join(lines) if lines else "No results found.",
        )
