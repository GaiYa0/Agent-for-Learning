"""Safe calculator tool — no eval, operator-based."""

import operator

from learning_assistant.models.tool import ToolResult
from learning_assistant.tools.base import BaseTool, ParameterSpec
from learning_assistant.tools.exceptions import ToolExecutionError, ToolValidationError

_OPERATORS: dict[str, object] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "%": operator.mod,
}


class CalculatorTool(BaseTool):
    """Performs basic arithmetic safely."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Perform basic arithmetic: +, -, *, /, %"

    @property
    def category(self) -> str:
        return "utility"

    @property
    def parameters(self) -> dict[str, ParameterSpec]:
        return {
            "expression": ParameterSpec(
                type="string",
                description="Arithmetic expression like '2 + 3' or '10 / 2'",
                required=True,
            ),
        }

    async def execute(self, **kwargs: str) -> ToolResult:
        expression = kwargs["expression"].strip()
        parts = expression.split()
        if len(parts) != 3:
            raise ToolValidationError(
                f"Expected format: 'a op b', got: '{expression}'"
            )
        left_str, op, right_str = parts
        try:
            left = float(left_str)
            right = float(right_str)
        except ValueError as e:
            raise ToolExecutionError(f"Invalid number in expression: {e}") from e
        func = _OPERATORS.get(op)
        if func is None:
            raise ToolExecutionError(
                f"Unsupported operator: '{op}'. Supported: {list(_OPERATORS.keys())}"
            )
        if op in ("/", "%") and right == 0:
            raise ToolExecutionError("Division by zero")
        result = func(left, right)  # type: ignore[operator]
        return ToolResult(
            tool_call_id="",
            success=True,
            content=str(result),
        )
