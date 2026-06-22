from app.core.config import settings
from app.services.llm import get_llm_client


def create_embeddings(texts: list[str]) -> list[list[float] | None]:
    if not texts:
        return []

    client = get_llm_client()
    if client is None:
        return [None] * len(texts)

    try:
        kwargs: dict[str, object] = {
            "model": settings.OPENAI_EMBEDDING_MODEL,
            "input": texts,
        }
        if settings.use_openai_embedding_dimensions:
            kwargs["dimensions"] = settings.EMBEDDING_DIMENSIONS
        response = client.embeddings.create(**kwargs)  # type: ignore[arg-type]
    except Exception:  # noqa: BLE001
        return [None] * len(texts)

    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]
