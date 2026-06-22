from openai import OpenAI

from app.core.config import settings


def get_llm_client() -> OpenAI | None:
    if not settings.llm_enabled:
        return None

    kwargs: dict[str, str] = {"api_key": settings.OPENAI_API_KEY or "ollama"}
    if settings.LLM_BASE_URL:
        kwargs["base_url"] = settings.LLM_BASE_URL
    return OpenAI(**kwargs)
