import uuid

from app.agents.rag_confidence import (
    assess_retrieval_confidence,
    classify_response_kind,
)
from app.services.retriever import RetrievedChunk


def test_assess_retrieval_confidence_no_chunks() -> None:
    result = assess_retrieval_confidence("help", [], max_score=None)
    assert result["confidence"] == "low"
    assert "no_chunks" in result["clarification_triggers"]
    assert result["clarification_recommended"] is False


def test_assess_retrieval_confidence_high_score() -> None:
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            document_title="Guide",
            content="Steps for card loss.",
            score=0.82,
        )
    ]
    result = assess_retrieval_confidence(
        "what do I do if I lost my card",
        chunks,
        max_score=0.82,
    )
    assert result["confidence"] == "high"
    assert result["clarification_triggers"] == []
    assert result["clarification_recommended"] is False


def test_assess_retrieval_confidence_multi_document_ambiguity() -> None:
    doc_a = uuid.uuid4()
    doc_b = uuid.uuid4()
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            document_id=doc_a,
            document_title="Card loss",
            content="Call to block.",
            score=0.71,
        ),
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            document_id=doc_b,
            document_title="PIN reset",
            content="Reset PIN in app.",
            score=0.69,
        ),
    ]
    result = assess_retrieval_confidence("card problem", chunks, max_score=0.71)
    assert "multi_document_ambiguity" in result["clarification_triggers"]
    assert result["clarification_recommended"] is True


def test_classify_response_kind_clarification() -> None:
    kind = classify_response_kind(
        "Did you lose the card, or do you need to reset your PIN?",
        clarification_recommended=True,
    )
    assert kind == "clarification"


def test_classify_response_kind_answer_when_not_recommended() -> None:
    kind = classify_response_kind(
        "Did you lose the card?",
        clarification_recommended=False,
    )
    assert kind == "answer"
