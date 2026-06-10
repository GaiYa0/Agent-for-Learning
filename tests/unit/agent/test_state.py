"""Tests for AgentRuntimeState and AgentAction."""

from learning_assistant.agent.state import AgentAction, AgentRuntimeState


class TestAgentAction:
    def test_default(self) -> None:
        a = AgentAction()
        assert a.is_final is False
        assert a.thought == ""

    def test_final_action(self) -> None:
        a = AgentAction(is_final=True, final_answer="42")
        assert a.is_final is True
        assert a.final_answer == "42"


class TestAgentRuntimeState:
    def test_can_continue_initial(self) -> None:
        s = AgentRuntimeState(max_iterations=5)
        assert s.can_continue() is True

    def test_can_continue_at_limit(self) -> None:
        s = AgentRuntimeState(iteration=5, max_iterations=5)
        assert s.can_continue() is False

    def test_can_continue_finished(self) -> None:
        s = AgentRuntimeState(is_finished=True, max_iterations=5)
        assert s.can_continue() is False

    def test_add_step(self) -> None:
        s = AgentRuntimeState(max_iterations=5)
        action = AgentAction(thought="thinking", action="search", action_input="q")
        s.add_step(action, observation="result")
        assert s.iteration == 1
        assert len(s.thoughts) == 1
        assert len(s.observations) == 1

    def test_add_final_step(self) -> None:
        s = AgentRuntimeState(max_iterations=5)
        action = AgentAction(is_final=True, final_answer="done")
        s.add_step(action)
        assert s.is_finished is True
        assert s.final_answer == "done"
