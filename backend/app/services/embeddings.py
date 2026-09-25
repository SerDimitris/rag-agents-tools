import logging

from app.core.config import settings
from app.services.llm import get_llm_client

logger = logging.getLogger(__name__)


def fit_embedding_to_column(embedding: list[float]) -> list[float] | None:
    size = settings.EMBEDDING_DIMENSIONS
    if len(embedding) == size:
        return embedding
    if len(embedding) < size:
        # Zero-padding preserves dot products and norms, so cosine distance is
        # unchanged. This lets smaller local models (e.g. nomic-embed-text, 768)
        # share the fixed-size pgvector column.
        return embedding + [0.0] * (size - len(embedding))
    logger.warning(
        "Embedding has %d dimensions but the vector column holds %d; "
        "falling back to keyword retrieval",
        len(embedding),
        size,
    )
    return None


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
        logger.warning(
            "Embedding request failed for model %s; falling back to keyword retrieval",
            settings.OPENAI_EMBEDDING_MODEL,
            exc_info=True,
        )
        return [None] * len(texts)

    ordered = sorted(response.data, key=lambda item: item.index)
    return [fit_embedding_to_column(item.embedding) for item in ordered]
