from app.core.config import settings
from app.services.llm import get_llm_client


def create_embeddings(texts: list[str]) -> list[list[float] | None]:
    if not texts:
        return []

    client = get_llm_client()
    if client is None:
        return [None] * len(texts)

    try:
        if settings.use_openai_embedding_dimensions:
            response = client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=texts,
                dimensions=settings.EMBEDDING_DIMENSIONS,
            )
        else:
            response = client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=texts,
            )
    except Exception:  # noqa: BLE001
        return [None] * len(texts)

    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]
