"""
Streamlit UI for the Market Analysis AI Agent.

Run with:
    .venv\\Scripts\\streamlit.exe run app.py
"""

import uuid

import streamlit as st

from src.agent.agent import build_agent

st.set_page_config(page_title="Market Agent", page_icon="📈", layout="centered")
st.title("📈 Market Analysis Agent")
st.caption("Ask questions about stocks — prices, history, volume, trends.")

# Build agent once per session; each session gets its own thread_id for memory isolation
if "agent" not in st.session_state:
    with st.spinner("Initialising agent…"):
        st.session_state.agent = build_agent()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"|"assistant", "content": str}

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("e.g. What is AAPL trading at? Show me TSLA's 14-day RSI.")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                result = st.session_state.agent.invoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config,
                )
                answer = result["messages"][-1].content
            except Exception as exc:
                answer = f"Error: {exc}"

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
