"""Scoped custom tools the PIA agent is allowed to call.

These are the ONLY actions available to the agent — no shell, no raw
filesystem, no web. They are LangChain @tool functions passed to the
LangGraph agent in agent.py. See spec §4.
"""
