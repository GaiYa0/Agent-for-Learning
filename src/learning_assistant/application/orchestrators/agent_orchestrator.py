"""Agent orchestrator — coordinates agent execution."""

from collections.abc import AsyncIterator

from learning_assistant.agent.core import ReActAgent
from learning_assistant.agent.executor import ActionExecutor
from learning_assistant.agent.mappers import build_agent_response
from learning_assistant.agent.memory import ConversationMemory
from learning_assistant.agent.planner import Planner
from learning_assistant.agent.state import AgentRuntimeState
from learning_assistant.agent.stream_events import StreamEvent
from learning_assistant.application.session.memory_manager import MemoryManager
from learning_assistant.models.agent import AgentResponse
from learning_assistant.models.rag import RAGCitation
from learning_assistant.tools.manager import ToolManager
from learning_assistant.tools.registry import ToolRegistry


class AgentOrchestrator:
    """Builds and runs agents with injected dependencies."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        planner: Planner,
        memory_manager: MemoryManager | None = None,
        max_iterations: int = 5,
        model: str = "",
    ) -> None:
        self._registry = tool_registry
        self._planner = planner
        self._memory_manager = memory_manager
        self._max_iterations = max_iterations
        self._model = model

    def build_agent(
        self,
        memory: ConversationMemory | None = None,
        max_iterations: int | None = None,
        tools_description: str = "",
        context: str = "",
    ) -> ReActAgent:
        manager = ToolManager(self._registry)
        executor = ActionExecutor(manager)
        return ReActAgent(
            planner=self._planner,
            executor=executor,
            memory=memory or ConversationMemory(),
            max_iterations=max_iterations or self._max_iterations,
            tools_description=tools_description,
            context=context,
        )

    async def run(
        self,
        question: str,
        context: str = "",
        session_id: str | None = None,
    ) -> AgentResponse:
        memory = self._resolve_memory(session_id)
        tool_desc = self._build_tool_description()
        agent = self.build_agent(
            memory=memory,
            tools_description=tool_desc,
            context=context,
        )
        answer = await agent.run(question)
        state = agent.get_last_state() or AgentRuntimeState(question=question)
        if session_id and self._memory_manager is not None:
            self._memory_manager.sync_to_store(session_id)
        return build_agent_response(
            answer=answer,
            state=state,
            events=agent.get_events(),
            model=self._model,
        )

    async def run_streaming(
        self,
        question: str,
        context: str = "",
        session_id: str | None = None,
        *,
        citations: list[RAGCitation] | None = None,
        retrieval_time_ms: int = 0,
    ) -> AsyncIterator[StreamEvent]:
        """Stream agent execution events; emits a final done event with metadata."""
        memory = self._resolve_memory(session_id)
        tool_desc = self._build_tool_description()
        agent = self.build_agent(
            memory=memory,
            tools_description=tool_desc,
            context=context,
        )
        async for event in agent.run_streaming(question, model=self._model):
            if event.kind == "done" and event.metadata is not None:
                if retrieval_time_ms:
                    event.metadata = event.metadata.model_copy(
                        update={"retrieval_time_ms": retrieval_time_ms}
                    )
                if citations:
                    event = StreamEvent(
                        kind="done",
                        answer=event.answer,
                        metadata=event.metadata,
                        citations=citations,
                    )
            yield event
        if session_id and self._memory_manager is not None:
            self._memory_manager.sync_to_store(session_id)

    def _resolve_memory(self, session_id: str | None) -> ConversationMemory:
        if session_id and self._memory_manager is not None:
            return self._memory_manager.get_memory(session_id)
        return ConversationMemory()

    def _build_tool_description(self) -> str:
        tools = self._registry.list_tools()
        return "\n".join(f"- {t.name}: {t.description}" for t in tools)
