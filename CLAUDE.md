# Market Analysis AI Agent

## Project goal
Agentic AI that answers stock market questions using the Massive API.

## Stack
- Python 3.11+
- LangChain + Anthropic Claude
- Massive API (real-time + historical stock data)
- Pandas for indicators (SMA, EMA, RSI)
- Streamlit for UI

## Folder structure
src/
  tools/       # LangChain tool definitions
  data/        # Massive API fetcher + indicators
  agent/       # ReAct agent loop + memory
app.py         # Streamlit entry point
tests/

## Rules
- All secrets in .env, never hardcoded
- Each tool must have a docstring Claude can use as the tool description
- Keep tools small and single-purpose