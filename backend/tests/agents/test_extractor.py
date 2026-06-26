import uuid
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from sqlmodel import Session

from app.agents.extractor import (
    _extract_with_llm,
    _fallback_summary,
    build_knowledge_context,
    run_document_extraction,
)
from app.models import Document, DocumentStatus
from app.services.embeddings import create_embeddings
from tests.utils.customer import create_random_customer


def test_create_embeddings_empty_list() -> None:
    assert create_embeddings([]) == []


def test_create_embeddings_without_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.embeddings.get_llm_client", lambda: None)
    assert create_embeddings(["one", "two"]) == [None, None]


def test_fallback_summary_truncates_long_text() -> None:
    summary = _fallback_summary("x" * 5000)
    assert "Automatic extraction" in summary
    assert len(summary) < 5000


def test_extract_with_llm_without_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agents.extractor.get_llm_client", lambda: None)
    summary = _extract_with_llm("Quarterly revenue increased.")
    assert "Automatic extraction" in summary


def test_extract_with_llm_uses_client_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices[
        0
    ].message.content = "  Structured summary  "
    monkeypatch.setattr("app.agents.extractor.get_llm_client", lambda: mock_client)

    summary = _extract_with_llm("Quarterly revenue increased.")
    assert summary == "Structured summary"


def test_build_knowledge_context_without_documents(db: Session) -> None:
    customer = create_random_customer(db)
    context = build_knowledge_context(db, customer.id)
    assert "No extracted document content" in context


def test_build_knowledge_context_with_summary(db: Session) -> None:
    customer = create_random_customer(db)
    document = Document(
        customer_id=customer.id,
        title="Policy Guide",
        file_path=f"uploads/{customer.id}/policy.txt",
        status=DocumentStatus.completed,
        extracted_data={"summary": "Customers can update PIN in the app."},
    )
    db.add(document)
    db.commit()

    context = build_knowledge_context(db, customer.id)
    assert "Policy Guide" in context
    assert "update PIN" in context


def test_run_document_extraction_success(
    db: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    customer = create_random_customer(db)
    upload_dir = tmp_path / str(customer.id)
    upload_dir.mkdir()
    stored_name = f"{uuid.uuid4()}_report.txt"
    file_path = upload_dir / stored_name
    file_path.write_text("Annual report content about cards.", encoding="utf-8")

    document = Document(
        customer_id=customer.id,
        title="Annual Report",
        file_path=f"uploads/{customer.id}/{stored_name}",
        status=DocumentStatus.pending,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    monkeypatch.setattr(
        "app.agents.extractor.resolve_upload_path",
        lambda _path: file_path,
    )
    monkeypatch.setattr("app.agents.extractor.get_llm_client", lambda: None)

    run_document_extraction(db, document.id)

    db.refresh(document)
    assert document.status == DocumentStatus.completed
    assert document.extracted_data is not None
    assert document.extracted_data["chunk_count"] >= 1


def test_run_document_extraction_missing_document(db: Session) -> None:
    run_document_extraction(db, uuid.uuid4())
