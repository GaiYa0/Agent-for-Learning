"""ReAct Agent — the main agent loop."""

import logging
from collections.abc import AsyncIterator

from learning_assistant.agent.events import (
    AgentEvent,
    AgentFinished,
    ThoughtGenerated,
    ToolCalled,
    ToolFinished,
)
from learning_assistant.agent.exceptions import ParseError
from learning_assistant.agent.executor import ActionExecutor
from learning_assistant.agent.mappers import build_agent_response
from learning_assistant.agent.memory import ConversationMemory
from learning_assistant.agent.planner import Planner
from learning_assistant.agent.state import AgentAction, AgentRuntimeState
from learning_assistant.agent.stream_events import StreamEvent

logger = logging.getLogger(__name__)


class ReActAgent:
    """Orchestrates the ReAct reasoning loop."""

    def __init__(
        self,
        planner: Planner,
        executor: ActionExecutor,
        memory: ConversationMemory | None = None,
        max_iterations: int = 5,
        tools_description: str = "",
        context: str = "",
    ) -> None:
        self._planner = planner
        self._executor = executor
        self._memory = memory or ConversationMemory()
        self._max_iterations = max_iterations
        self._tools_description = tools_description
        self._context = context
        self._events: list[AgentEvent] = []
        self._last_state: AgentRuntimeState | None = None

    async def run(self, question: str) -> str:
        state = AgentRuntimeState(
            question=question, max_iterations=self._max_iterations
        )
        self._last_state = state
        self._memory.add_user_message(question)
        self._events.clear()

        while state.can_continue():
            try:
                action = await self._planner.plan(
                    question=question,
                    tools_description=self._tools_description,
                    history=self._memory.get_messages(),
                    observations=self._format_observations(state),
                    context=self._context,
                )
            except ParseError as exc:
                retry_action = AgentAction(
                    thought="Failed to parse LLM output.",
                    action="parse_error",
                )
                observation = (
                    f"Parse error: {exc}. "
                    "Respond using Thought/Action/Action Input or Final Answer format."
                )
                state.add_step(retry_action, observation)
                continue

            self._emit(
                ThoughtGenerated(iteration=state.iteration, thought=action.thought)
            )

            if action.is_final:
                state.add_step(action)
                self._memory.add_assistant_message(action.final_answer)
                self._emit(
                    AgentFinished(
                        iteration=state.iteration,
                        final_answer=action.final_answer,
                        total_iterations=state.iteration,
                    )
                )
                return action.final_answer

            observation, success = await self._execute_action(state.iteration, action)
            state.add_step(action, observation)

        return state.final_answer or "I was unable to determine an answer."

    async def run_streaming(
        self, question: str, *, model: str = ""
    ) -> AsyncIterator[StreamEvent]:
        """Run the ReAct loop, streaming LLM tokens and tool status events."""
        state = AgentRuntimeState(
            question=question, max_iterations=self._max_iterations
        )
        self._last_state = state
        self._memory.add_user_message(question)
        self._events.clear()

        while state.can_continue():
            action: AgentAction | None = None
            try:
                async for item in self._planner.plan_stream(
                    question=question,
                    tools_description=self._tools_description,
                    history=self._memory.get_messages(),
                    observations=self._format_observations(state),
                    context=self._context,
                ):
                    if isinstance(item, str):
                        yield StreamEvent(kind="token", content=item)
                    else:
                        action = item
            except ParseError as exc:
                retry_action = AgentAction(
                    thought="Failed to parse LLM output.",
                    action="parse_error",
                )
                observation = (
                    f"Parse error: {exc}. "
                    "Respond using Thought/Action/Action Input or Final Answer format."
                )
                state.add_step(retry_action, observation)
                continue

            if action is None:
                continue

            self._emit(
                ThoughtGenerated(iteration=state.iteration, thought=action.thought)
            )

            if action.is_final:
                state.add_step(action)
                self._memory.add_assistant_message(action.final_answer)
                self._emit(
                    AgentFinished(
                        iteration=state.iteration,
                        final_answer=action.final_answer,
                        total_iterations=state.iteration,
                    )
                )
                response = build_agent_response(
                    answer=action.final_answer,
                    state=state,
                    events=self._events,
                    model=model,
                )
                yield StreamEvent(
                    kind="done",
                    answer=action.final_answer,
                    metadata=response.metadata,
                )
                return

            yield StreamEvent(
                kind="tool_start",
                tool_name=action.action,
                content=action.action_input,
            )
            observation, _success = await self._execute_action(
                state.iteration, action
            )
            yield StreamEvent(
                kind="tool_end",
                tool_name=action.action,
                content=observation,
            )
            state.add_step(action, observation)

        fallback = state.final_answer or "I was unable to determine an answer."
        response = build_agent_response(
            answer=fallback,
            state=state,
            events=self._events,
            model=model,
        )
        yield StreamEvent(kind="done", answer=fallback, metadata=response.metadata)

    async def _execute_action(
        self, iteration: int, action: AgentAction
    ) -> tuple[str, bool]:
        self._emit(
            ToolCalled(
                iteration=iteration,
                tool_name=action.action,
                tool_input=action.action_input,
            )
        )
        observation, success = await self._executor.execute_or_default(
            action.action, action.action_input
        )
        self._memory.add_tool_message(observation)
        self._emit(
            ToolFinished(
                iteration=iteration,
                tool_name=action.action,
                observation=observation,
                success=success,
            )
        )
        return observation, success

    def _format_observations(self, state: AgentRuntimeState) -> str:
        if not state.observations:
            return "None yet."
        lines: list[str] = []
        for i, obs in enumerate(state.observations):
            action = state.actions[i] if i < len(state.actions) else None
            tool = action.action if action else "unknown"
            lines.append(f"Observation {i + 1} ({tool}): {obs}")
        return "\n".join(lines)

    def _emit(self, event: AgentEvent) -> None:
        self._events.append(event)

    def get_events(self) -> list[AgentEvent]:
        return list(self._events)

    def get_memory(self) -> ConversationMemory:
        return self._memory

    def get_last_state(self) -> AgentRuntimeState | None:
        return self._last_state
