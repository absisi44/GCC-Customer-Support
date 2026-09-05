# ======================================================
# LLM Provider Factory
# ======================================================
# pyrefly: ignore [missing-import]
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0):
    """
    Returns an initialized chat LLM.
    Uses OpenAI (gpt-4o-mini) when OPENAI_API_KEY is set,
    or falls back to Groq if GROQ_API_KEY is present.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if openai_key:
        openai_key = openai_key.strip().splitlines()[0].strip()
    if groq_key:
        groq_key = groq_key.strip().splitlines()[0].strip()

    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "groq" and groq_key:
        from langchain_groq import ChatGroq
        model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        return ChatGroq(
            model_name=model_name,
            temperature=temperature,
            groq_api_key=groq_key,
            max_tokens=700,
        )
    elif openai_key:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature, api_key=openai_key)
    elif groq_key:
        from langchain_groq import ChatGroq
        model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        return ChatGroq(
            model_name=model_name,
            temperature=temperature,
            groq_api_key=groq_key,
            max_tokens=700,
        )
    else:
        raise ValueError("Neither OPENAI_API_KEY nor GROQ_API_KEY found in environment variables.")
