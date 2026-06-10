"""Agent runtime state — tracks the evolving state of a single agent run."""

from dataclasses import dataclass, field

from learning_assistant.models.tool import ToolCall


@dataclass
class AgentAction:
    """A parsed action from the LLM output."""

    thought: str = ""
    action: str = ""
    action_input: str = ""
    is_final: bool = False
    final_answer: str = ""


@dataclass
class AgentRuntimeState:
    """Mutable state for a single agent run."""

    question: str = ""
    thoughts: list[str] = field(default_factory=list)
    actions: list[AgentAction] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 5
    is_finished: bool = False
    final_answer: str = ""

    def can_continue(self) -> bool:
        return not self.is_finished and self.iteration < self.max_iterations

    def add_step(self, action: AgentAction, observation: str = "") -> None:
        self.thoughts.append(action.thought)
        self.actions.append(action)
        if observation:
            self.observations.append(observation)
        self.iteration += 1
        if action.is_final:
            self.is_finished = True
            self.final_answer = action.final_answer
