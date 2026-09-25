import math
from unittest.mock import MagicMock

import pytest

from app.core.config import settings
from app.services.embeddings import create_embeddings, fit_embedding_to_column


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def test_fit_embedding_keeps_exact_size() -> None:
    embedding = [0.1] * settings.EMBEDDING_DIMENSIONS
    assert fit_embedding_to_column(embedding) == embedding


def test_fit_embedding_pads_smaller_model_without_changing_cosine() -> None:
    a = [0.3, -0.2, 0.9, 0.1]
    b = [0.1, 0.4, 0.5, -0.7]
    padded_a = fit_embedding_to_column(a)
    padded_b = fit_embedding_to_column(b)

    assert padded_a is not None and padded_b is not None
    assert len(padded_a) == settings.EMBEDDING_DIMENSIONS
    assert _cosine(padded_a, padded_b) == pytest.approx(_cosine(a, b))


def test_fit_embedding_rejects_oversized_model() -> None:
    assert fit_embedding_to_column([0.1] * (settings.EMBEDDING_DIMENSIONS + 1)) is None


def test_create_embeddings_returns_none_when_request_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = RuntimeError("model not found")
    monkeypatch.setattr("app.services.embeddings.get_llm_client", lambda: mock_client)

    assert create_embeddings(["one", "two"]) == [None, None]


def test_create_embeddings_pads_and_orders_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    second = MagicMock(index=1, embedding=[0.0, 1.0])
    first = MagicMock(index=0, embedding=[1.0, 0.0])
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value.data = [second, first]
    monkeypatch.setattr("app.services.embeddings.get_llm_client", lambda: mock_client)

    result = create_embeddings(["first", "second"])

    assert [vector[:2] for vector in result if vector is not None] == [
        [1.0, 0.0],
        [0.0, 1.0],
    ]
    assert all(
        vector is not None and len(vector) == settings.EMBEDDING_DIMENSIONS
        for vector in result
    )
