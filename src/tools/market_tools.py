"""
LangChain tool definitions that expose Massive API data to the ReAct agent.

Each tool is intentionally single-purpose so the agent can compose them freely.
Docstrings are written for Claude — they become the tool description the model
reads when deciding which tool to call.
"""

import json

from langchain_core.tools import tool

from src.data.fetcher import get_ohlcv, get_quote, get_volume


@tool
def quote_tool(ticker: str) -> str:
    """
    Get the latest real-time quote for a stock ticker.

    Returns current price, bid, ask, intraday change (absolute and percent),
    and today's volume. Use this when the user asks about the current price
    or how a stock is doing right now.

    Args:
        ticker: Stock symbol in uppercase, e.g. 'AAPL', 'TSLA', 'MSFT'.
    """
    data = get_quote(ticker.upper())
    return json.dumps(data, default=str)


@tool
def ohlcv_tool(ticker: str, days: int = 30) -> str:
    """
    Get daily OHLCV (open, high, low, close, volume) bars for a stock.

    Returns a JSON list of daily bars ordered oldest-first. Use this when
    the user asks about price history, trends over time, or when you need
    data for technical indicator calculations (SMA, EMA, RSI, etc.).

    Args:
        ticker: Stock symbol in uppercase, e.g. 'AAPL'.
        days:   Number of calendar days of history to fetch (default 30).
    """
    bars = get_ohlcv(ticker.upper(), days=days)
    return json.dumps(bars, default=str)


@tool
def volume_tool(ticker: str) -> str:
    """
    Get the most recent single-day trading volume for a stock.

    Returns the volume as a plain integer string. Use this when the user
    asks specifically about trading volume or liquidity without needing
    full price history.

    Args:
        ticker: Stock symbol in uppercase, e.g. 'AAPL'.
    """
    vol = get_volume(ticker.upper())
    return str(vol)


# Collected list — import this in the agent
MARKET_TOOLS = [quote_tool, ohlcv_tool, volume_tool]
