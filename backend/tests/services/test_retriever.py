import uuid

from sqlmodel import Session

from app.models import Document, DocumentStatus
from app.services.retriever import (
    RetrievedChunk,
    format_retrieved_context,
    index_document_chunks,
    retrieve_knowledge_context,
    retrieve_relevant_chunks,
)
from tests.utils.customer import create_random_customer


def test_format_retrieved_context_empty() -> None:
    assert "No extracted document content" in format_retrieved_context([])


def test_format_retrieved_context_with_chunks() -> None:
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            document_title="Annual Report",
            content="Revenue grew 12%.",
            score=0.9,
        )
    ]
    context = format_retrieved_context(chunks)
    assert "### Annual Report" in context
    assert "Revenue grew 12%." in context


def test_index_and_retrieve_by_keywords(db: Session) -> None:
    customer = create_random_customer(db)
    document = Document(
        customer_id=customer.id,
        title="Banking FAQ",
        file_path=f"uploads/{customer.id}/faq.txt",
        status=DocumentStatus.completed,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    raw_text = (
        "Question: How do I block my card?\n"
        "Answer: Call support at 210 1234567 immediately."
    )
    chunk_count = index_document_chunks(db, document.id, raw_text)
    assert chunk_count >= 1

    result = retrieve_relevant_chunks(
        db, "How do I block my card?", customer.id, top_k=3
    )
    assert result.expanded_queries
    assert result.chunks
    assert any("block" in chunk.content.lower() for chunk in result.chunks)

    knowledge = retrieve_knowledge_context(
        db, "How do I block my card?", customer.id
    )
    assert "block" in knowledge.lower()
