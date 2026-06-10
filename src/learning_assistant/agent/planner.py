"""Planner — generates the next Thought and decides the next Action."""

from collections.abc import AsyncIterator

from learning_assistant.agent.llm.base import BaseLLM
from learning_assistant.agent.parser import ReActParser
from learning_assistant.agent.state import AgentAction
from learning_assistant.models.chat import ChatMessage
from learning_assistant.prompts.react_prompt import ReActPrompt


class Planner:
    """Drives the ReAct loop by prompting the LLM and parsing its output."""

    def __init__(
        self,
        llm: BaseLLM,
        parser: ReActParser | None = None,
        prompt: ReActPrompt | None = None,
    ) -> None:
        self._llm = llm
        self._parser = parser or ReActParser()
        self._prompt = prompt or ReActPrompt()

    async def plan(
        self,
        question: str,
        tools_description: str,
        history: list[ChatMessage],
        observations: str,
        context: str = "",
    ) -> AgentAction:
        prompt = self._build_prompt(question, tools_description, observations, context)
        messages = self._format_messages(history, prompt)
        response = await self._llm.generate(messages)
        return self._parser.parse(response.content)

    async def plan_stream(
        self,
        question: str,
        tools_description: str,
        history: list[ChatMessage],
        observations: str,
        context: str = "",
    ) -> AsyncIterator[str | AgentAction]:
        """Stream LLM tokens, then yield the parsed AgentAction as the final item."""
        prompt = self._build_prompt(question, tools_description, observations, context)
        messages = self._format_messages(history, prompt)
        buffer: list[str] = []
        async for token in self._llm.stream_tokens(messages):
            buffer.append(token)
            yield token
        yield self._parser.parse("".join(buffer))

    def _build_prompt(
        self,
        question: str,
        tools_description: str,
        observations: str,
        context: str,
    ) -> str:
        context_block = f"Context:\n{context}" if context else ""
        return self._prompt.build(
            question=question,
            tools=tools_description,
            observations=observations,
            context=context_block,
        )

    def _format_messages(
        self, history: list[ChatMessage], prompt: str
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": "You are a helpful learning assistant."}
        ]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": prompt})
        return messages
