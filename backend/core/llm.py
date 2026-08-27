from langchain_groq import ChatGroq
from groq import Groq
import instructor
from .config import settings


def get_chat_llm(temperature: float = 0.1, max_tokens: int = 2048) -> ChatGroq:
    """
    Returns a LangChain-compatible ChatGroq LLM.
    Used by agents for async LLM calls via .ainvoke().
    """
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def get_instructor_client():
    """
    Returns an Instructor-patched Groq client.
    Used by the Orchestrator for structured JSON output (SpawnManifest).
    Instructor forces the LLM to return a valid Pydantic model.
    """
    raw_client = Groq(api_key=settings.GROQ_API_KEY)
    return instructor.from_groq(raw_client, mode=instructor.Mode.JSON)
