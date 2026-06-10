"""Helpers for Server-Sent Events streaming responses."""

import json

from learning_assistant.agent.stream_events import StreamEvent


def stream_event_to_sse(event: StreamEvent) -> str:
    """Format a StreamEvent as an SSE data line."""
    return f"data: {json.dumps(event.to_sse_payload())}\n\n"
