"""Agent-layer exception hierarchy."""


class AgentError(Exception):
    """Base for all agent errors."""


class MaxIterationsError(AgentError):
    """Raised when the agent exceeds its iteration limit."""


class ParseError(AgentError):
    """Raised when LLM output cannot be parsed."""


class PlannerError(AgentError):
    """Raised when the planner fails."""


class ExecutorError(AgentError):
    """Raised when action execution fails."""
