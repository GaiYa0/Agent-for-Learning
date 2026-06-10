"""Tests for CalculatorTool."""

import pytest

from learning_assistant.tools.calculator_tool import CalculatorTool
from learning_assistant.tools.exceptions import ToolExecutionError, ToolValidationError


@pytest.fixture()
def tool() -> CalculatorTool:
    return CalculatorTool()


class TestCalculatorTool:
    def test_name(self, tool: CalculatorTool) -> None:
        assert tool.name == "calculator"

    def test_category(self, tool: CalculatorTool) -> None:
        assert tool.category == "utility"

    @pytest.mark.asyncio
    async def test_addition(self, tool: CalculatorTool) -> None:
        result = await tool.execute(expression="2 + 3")
        assert result.is_success()
        assert result.content == "5.0"

    @pytest.mark.asyncio
    async def test_subtraction(self, tool: CalculatorTool) -> None:
        result = await tool.execute(expression="10 - 4")
        assert result.content == "6.0"

    @pytest.mark.asyncio
    async def test_multiplication(self, tool: CalculatorTool) -> None:
        result = await tool.execute(expression="3 * 7")
        assert result.content == "21.0"

    @pytest.mark.asyncio
    async def test_division(self, tool: CalculatorTool) -> None:
        result = await tool.execute(expression="10 / 4")
        assert result.content == "2.5"

    @pytest.mark.asyncio
    async def test_modulo(self, tool: CalculatorTool) -> None:
        result = await tool.execute(expression="10 % 3")
        assert result.content == "1.0"

    @pytest.mark.asyncio
    async def test_division_by_zero(self, tool: CalculatorTool) -> None:
        with pytest.raises(ToolExecutionError, match="Division by zero"):
            await tool.execute(expression="1 / 0")

    @pytest.mark.asyncio
    async def test_modulo_by_zero(self, tool: CalculatorTool) -> None:
        with pytest.raises(ToolExecutionError, match="Division by zero"):
            await tool.execute(expression="10 % 0")

    @pytest.mark.asyncio
    async def test_invalid_format(self, tool: CalculatorTool) -> None:
        with pytest.raises(ToolValidationError, match="Expected format"):
            await tool.execute(expression="1+2+3")

    @pytest.mark.asyncio
    async def test_invalid_number(self, tool: CalculatorTool) -> None:
        with pytest.raises(ToolExecutionError, match="Invalid number"):
            await tool.execute(expression="abc + 1")

    @pytest.mark.asyncio
    async def test_unsupported_operator(self, tool: CalculatorTool) -> None:
        with pytest.raises(ToolExecutionError, match="Unsupported operator"):
            await tool.execute(expression="2 ^ 3")

    def test_schema(self, tool: CalculatorTool) -> None:
        s = tool.schema()
        assert "expression" in s["parameters"]["properties"]
