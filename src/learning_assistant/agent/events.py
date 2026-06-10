"""Agent events — emitted during agent runs for observability."""

from dataclasses import dataclass


@dataclass
class AgentEvent:
    """Base for all agent events."""

    iteration: int


@dataclass
class ThoughtGenerated(AgentEvent):
    thought: str = ""


@dataclass
class ToolCalled(AgentEvent):
    tool_name: str = ""
    tool_input: str = ""


@dataclass
class ToolFinished(AgentEvent):
    tool_name: str = ""
    observation: str = ""
    success: bool = True


@dataclass
class AgentFinished(AgentEvent):
    final_answer: str = ""
    total_iterations: int = 0
