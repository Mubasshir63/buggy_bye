import os

from langchain_ollama import ChatOllama


def get_chat_model():
    """Return the configured language model."""

    provider = os.getenv(
        "BUGHUNTER_LLM_PROVIDER",
        "ollama",
    ).lower()

    if provider == "ollama":
        return ChatOllama(
            model=os.getenv(
                "BUGHUNTER_OLLAMA_MODEL",
                "qwen2.5-coder:3b",
            ),
            temperature=0,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "Set OPENAI_API_KEY to use the OpenAI provider."
            )

        return ChatOpenAI(
            model=os.getenv(
                "BUGHUNTER_OPENAI_MODEL",
                "gpt-4o-mini",
            ),
            temperature=0,
        )

    raise ValueError(
        f"Unsupported LLM provider: {provider}. "
        "Choose 'ollama' or 'openai'."
    )


if __name__ == "__main__":
    print("Initializing BugHunter AI LLM...")

    model = get_chat_model()

    response = model.invoke(
        "A Python addition function returns a - b instead of a + b. "
        "Explain the likely bug and suggest the correct expression. "
        "Keep your answer concise."
    )

    print("\n[BUGHUNTER AI RESPONSE]")
    print(response.content)