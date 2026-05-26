"""
Conversation memory for the ReAct agent.

Uses LangGraph's MemorySaver, which persists the full message graph
in-memory keyed by thread_id. Each Streamlit session gets its own
thread_id so conversations are isolated.
"""

from langgraph.checkpoint.memory import MemorySaver


def build_memory() -> MemorySaver:
    """Return a fresh in-memory checkpointer for LangGraph."""
    return MemorySaver()
