"""Tool manager — executes tools with unified error handling and logging."""

import logging
import time

from learning_assistant.models.tool import ToolResult
from learning_assistant.tools.base import BaseTool
from learning_assistant.tools.exceptions import ToolValidationError
from learning_assistant.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolManager:
    """Orchestrates tool execution via a registry."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def execute(self, tool: BaseTool, **kwargs: str) -> ToolResult:
        start = time.monotonic()
        try:
            tool.validate(**kwargs)
        except ToolValidationError:
            raise
        except Exception as e:
            raise ToolValidationError(str(e)) from e
        try:
            result = await tool.execute(**kwargs)
        except ToolValidationError:
            raise
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            logger.exception("Tool '%s' execution failed", tool.name)
            return ToolResult(
                tool_call_id="",
                success=False,
                content="",
                error=str(e),
                duration_ms=elapsed,
            )
        elapsed = int((time.monotonic() - start) * 1000)
        logger.info("Tool '%s' completed in %dms", tool.name, elapsed)
        return ToolResult(
            tool_call_id=result.tool_call_id,
            success=result.success,
            content=result.content,
            error=result.error,
            duration_ms=elapsed,
        )

    async def execute_by_name(self, name: str, **kwargs: str) -> ToolResult:
        tool = self._registry.get(name)
        if "input" in kwargs and tool.primary_parameter not in kwargs:
            remapped = dict(kwargs)
            remapped[tool.primary_parameter] = remapped.pop("input")
            kwargs = remapped
        return await self.execute(tool, **kwargs)
