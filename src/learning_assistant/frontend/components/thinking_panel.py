"""Thinking panel component — displays ReAct reasoning steps."""

from learning_assistant.frontend.i18n.strings import UIStrings


def render_thinking_panel(thinking: str, t: UIStrings) -> None:
    import streamlit as st

    if not thinking:
        return
    with st.expander(t.agent_thinking, expanded=False):
        for line in thinking.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("Thought:"):
                st.markdown(f"**{t.react_thought}:** {line[8:].strip()}")
            elif line.startswith("Action:"):
                st.markdown(f"**{t.react_action}:** {line[7:].strip()}")
            elif line.startswith("Observation:"):
                st.markdown(f"**{t.react_observation}:** {line[12:].strip()}")
            elif line.startswith("Final Answer:"):
                st.markdown(f"**{t.react_final_answer}:** {line[13:].strip()}")
            else:
                st.text(line)
