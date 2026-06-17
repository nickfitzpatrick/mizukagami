"""Model access layer — the pluggable, model-agnostic core (spec §3, §7).

Returns a LangChain chat model. The SAME agent graph runs against either a
local Ollama model (free, private) or the Claude API (frontier quality),
selected by env. This is the open-weight goal as a runtime choice.

    MIZUKAGAMI_MODEL_PROVIDER=ollama    -> local (default)
    MIZUKAGAMI_MODEL_PROVIDER=anthropic -> Claude API (needs ANTHROPIC_API_KEY)

Imports are done lazily inside each branch so you only need the package for
the provider you actually use.
"""

from __future__ import annotations

import os

OLLAMA_MODEL = os.environ.get("MIZUKAGAMI_OLLAMA_MODEL", "llama3.1:8b")
ANTHROPIC_MODEL = os.environ.get("MIZUKAGAMI_ANTHROPIC_MODEL", "claude-sonnet-4-6")


def get_provider() -> str:
    return os.environ.get("MIZUKAGAMI_MODEL_PROVIDER", "ollama").lower()


def get_chat_model():
    """Return a LangChain chat model based on env config."""
    provider = get_provider()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=OLLAMA_MODEL, temperature=0)

    if provider == "anthropic":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError(
                "MIZUKAGAMI_MODEL_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set."
            )
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)

    raise ValueError(
        f"Unknown MIZUKAGAMI_MODEL_PROVIDER: {provider!r} (use 'ollama' or 'anthropic')"
    )


def describe() -> str:
    """Human-readable one-liner of the active model, for the CLI banner."""
    provider = get_provider()
    model = OLLAMA_MODEL if provider == "ollama" else ANTHROPIC_MODEL
    return f"{provider}:{model}"


# M3: add get_embeddings() here (Ollama-served or hosted).
