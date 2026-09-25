from functools import lru_cache

from openai import OpenAI

from app.core.config import settings


@lru_cache(maxsize=4)
def _build_client(api_key: str, base_url: str | None, timeout: float) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=1)


def get_llm_client() -> OpenAI | None:
    if not settings.llm_enabled:
        return None

    api_key = settings.OPENAI_API_KEY or "ollama"
    return _build_client(api_key, settings.LLM_BASE_URL, settings.LLM_TIMEOUT_SECONDS)
