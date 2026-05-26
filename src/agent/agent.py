"""
ReAct agent loop backed by Claude and the Massive API market tools.

Usage:
    from src.agent.agent import build_agent
    agent = build_agent()
    config = {"configurable": {"thread_id": "my-session"}}
    result = agent.invoke({"messages": [{"role": "user", "content": "What is AAPL trading at?"}]}, config)
    print(result["messages"][-1].content)
"""

import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from src.agent.memory import build_memory
from src.tools.market_tools import MARKET_TOOLS

load_dotenv()

_SYSTEM_PROMPT = (
    "You are a market analysis assistant with access to real-time and historical "
    "stock data. Use the tools available to answer the user's question accurately. "
    "Always state the ticker symbol and data timestamp when reporting prices."
)


def build_agent(model: str = "claude-sonnet-4-6", temperature: float = 0):
    """
    Build and return a LangGraph ReAct agent wired to Claude + market tools.

    Args:
        model:       Anthropic model ID to use.
        temperature: Sampling temperature (0 = deterministic).
    """
    llm = ChatAnthropic(
        model=model,
        temperature=temperature,
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
    )
    return create_react_agent(
        model=llm,
        tools=MARKET_TOOLS,
        prompt=SystemMessage(content=_SYSTEM_PROMPT),
        checkpointer=build_memory(),
    )
