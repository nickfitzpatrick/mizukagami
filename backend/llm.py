"""Model access layer — the pluggable, model-agnostic core (spec §3, §7).

Returns a LangChain chat model. The SAME agent graph runs against either
a local Ollama model (free, private) or the Claude API (frontier quality),
selected by the MIZUKAGAMI_MODEL_PROVIDER env var. This is the open-weight
goal realized as a runtime choice, not a deferred swap.

    MIZUKAGAMI_MODEL_PROVIDER=ollama    -> local (default for dev)
    MIZUKAGAMI_MODEL_PROVIDER=anthropic -> Claude API (needs ANTHROPIC_API_KEY)
"""

import os

OLLAMA_MODEL = os.environ.get("MIZUKAGAMI_OLLAMA_MODEL", "llama3.1:8b")
ANTHROPIC_MODEL = os.environ.get("MIZUKAGAMI_ANTHROPIC_MODEL", "claude-sonnet-4-6")


def get_chat_model():
    """Return a LangChain chat model based on env config."""
    provider = os.environ.get("MIZUKAGAMI_MODEL_PROVIDER", "ollama").lower()

    if provider == "ollama":
        # from langchain_ollama import ChatOllama
        # return ChatOllama(model=OLLAMA_MODEL, temperature=0)
        raise NotImplementedError("M1: wire up ChatOllama")

    if provider == "anthropic":
        # from langchain_anthropic import ChatAnthropic
        # return ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)
        raise NotImplementedError("M1: wire up ChatAnthropic")

    raise ValueError(f"Unknown MIZUKAGAMI_MODEL_PROVIDER: {provider!r}")


# M3: add get_embeddings() here (Ollama-served or hosted).
