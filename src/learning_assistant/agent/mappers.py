"""Maps runtime agent state to domain models."""

from learning_assistant.agent.events import AgentEvent, ToolCalled
from learning_assistant.agent.memory import ConversationMemory
from learning_assistant.agent.state import AgentRuntimeState
from learning_assistant.models.agent import AgentResponse, AgentState, ResponseMetadata
from learning_assistant.models.chat import Conversation


def runtime_to_agent_state(
    state: AgentRuntimeState,
    memory: ConversationMemory,
) -> AgentState:
    """Convert mutable runtime state to domain AgentState."""
    tools_used: list[str] = []
    seen: set[str] = set()
    for action in state.actions:
        if action.action and not action.is_final and action.action not in seen:
            seen.add(action.action)
            tools_used.append(action.action)

    domain = AgentState(
        conversation=Conversation(messages=memory.get_messages()),
        iteration=state.iteration,
        max_iterations=state.max_iterations,
        tools_used=tools_used,
    )
    return domain


def tools_used_from_events(events: list[AgentEvent]) -> list[str]:
    """Extract unique tool names from agent events."""
    tools: list[str] = []
    seen: set[str] = set()
    for event in events:
        if isinstance(event, ToolCalled) and event.tool_name not in seen:
            seen.add(event.tool_name)
            tools.append(event.tool_name)
    return tools


def build_agent_response(
    answer: str,
    state: AgentRuntimeState,
    events: list[AgentEvent],
    *,
    model: str = "",
    total_duration_ms: int = 0,
) -> AgentResponse:
    """Build domain AgentResponse from a completed agent run."""
    metadata = ResponseMetadata(
        iterations=state.iteration,
        tools_used=tools_used_from_events(events),
        total_duration_ms=total_duration_ms,
        model=model,
    )
    return AgentResponse(answer=answer, metadata=metadata)
