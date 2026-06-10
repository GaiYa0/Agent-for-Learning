"""Search use case — executes a web search via tools."""

import re

from learning_assistant.application.dto.common import Result
from learning_assistant.application.dto.search_request import (
    SearchRequest,
    SearchResponseDTO,
)
from learning_assistant.application.orchestrators.tool_orchestrator import ToolOrchestrator
from learning_assistant.application.usecases.base import BaseUseCase
from learning_assistant.models.search import SearchResult

_SEARCH_LINE = re.compile(r"^\[(.+?)\]\((.+?)\): (.*)$")


def _parse_search_results(content: str) -> list[SearchResult]:
    results: list[SearchResult] = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line == "No results found.":
            continue
        match = _SEARCH_LINE.match(line)
        if match:
            results.append(
                SearchResult(
                    title=match.group(1),
                    url=match.group(2),
                    snippet=match.group(3),
                )
            )
    return results


class SearchUseCase(BaseUseCase[SearchRequest, SearchResponseDTO]):
    """Executes a web search."""

    def __init__(self, tool_orchestrator: ToolOrchestrator) -> None:
        self._tool = tool_orchestrator

    async def execute(self, input_dto: SearchRequest) -> Result[SearchResponseDTO]:
        try:
            tool_result = await self._tool.execute(
                "web_search",
                input=input_dto.query,
                max_results=str(input_dto.max_results),
            )
            results = _parse_search_results(tool_result.content)
            return Result.ok(
                SearchResponseDTO(
                    query=input_dto.query,
                    results=results,
                    provider="tool",
                )
            )
        except Exception as e:
            return Result.fail(str(e))
