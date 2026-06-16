"""Scoped custom tools the PIA agent is allowed to call.

These are the ONLY actions available to the agent — no raw file or shell
access. They are exposed as an in-process MCP server (see agent.py) and
referenced in allowed_tools as mcp__pia__<tool_name>. See spec §4.
"""
