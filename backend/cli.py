"""M1 entry point: talk to the Mizukagami agent in the terminal.

Proves the agent harness end-to-end before any backend or UI.

Run (from backend/):
    python cli.py
Pick the model via env (see ../.env.example):
    MIZUKAGAMI_MODEL_PROVIDER=ollama python cli.py
    MIZUKAGAMI_MODEL_PROVIDER=anthropic python cli.py
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

import llm
from agent import build_agent


def _print_stream(agent, user_text: str) -> None:
    """Stream agent steps, surfacing tool calls and the final answer."""
    for step in agent.stream(
        {"messages": [HumanMessage(content=user_text)]},
        stream_mode="values",
    ):
        msg = step["messages"][-1]
        if isinstance(msg, AIMessage):
            for call in msg.tool_calls or []:
                print(f"  · {call['name']}({call['args']})")
            if msg.content:
                print(f"\nmizukagami> {msg.content}\n")
        elif isinstance(msg, ToolMessage):
            pass  # tool output is internal; comment in to debug


def main() -> None:
    print(f"Mizukagami CLI — model: {llm.describe()}")
    print("Type a question, or 'exit' to quit.\n")
    agent = build_agent()
    while True:
        try:
            user_text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_text.lower() in {"exit", "quit"}:
            break
        if not user_text:
            continue
        _print_stream(agent, user_text)


if __name__ == "__main__":
    main()
