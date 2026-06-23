import uuid

from sqlmodel import Session, select

from app.core.config import settings
from app.models import Document, DocumentStatus
from app.services.file_storage import resolve_upload_path
from app.services.file_text import read_text_from_file
from app.services.llm import get_llm_client
from app.services.retriever import index_document_chunks

EXTRACTION_PROMPT = """You are a document extraction agent. Analyze the following document content and extract the most important information.

Include:
- A concise summary of the document
- Key topics and themes
- Important facts, figures, or entities mentioned
- Any actionable items or conclusions

Respond in clear, structured prose. Do not ask the user questions.

Document content:
{content}
"""


def _fallback_summary(raw_text: str) -> str:
    preview = raw_text.strip()
    if len(preview) > 4000:
        preview = preview[:4000] + "..."
    return (
        "Automatic extraction (no LLM configured). "
        "Preview of document content:\n\n" + preview
    )


def _extract_with_llm(raw_text: str) -> str:
    client = get_llm_client()
    if client is None:
        return _fallback_summary(raw_text)

    truncated = raw_text
    if len(truncated) > 120000:
        truncated = truncated[:120000]

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": EXTRACTION_PROMPT.format(content=truncated),
            }
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content
    return content.strip() if content else _fallback_summary(raw_text)


def run_document_extraction(session: Session, document_id: uuid.UUID) -> None:
    document = session.get(Document, document_id)
    if not document:
        return

    document.status = DocumentStatus.processing
    session.add(document)
    session.commit()
    session.refresh(document)

    try:
        file_path = resolve_upload_path(document.file_path)
        raw_text = read_text_from_file(file_path)
        if not raw_text.strip():
            raise ValueError("No text could be extracted from the uploaded file")

        summary = _extract_with_llm(raw_text)
        chunk_count = index_document_chunks(session, document_id, raw_text)
        document.extracted_data = {
            "summary": summary,
            "raw_text": raw_text[:50000],
            "filename": file_path.name,
            "chunk_count": chunk_count,
        }
        document.status = DocumentStatus.completed
    except Exception as exc:  # noqa: BLE001
        document.status = DocumentStatus.failed
        document.extracted_data = {"error": str(exc)}
    finally:
        session.add(document)
        session.commit()


def build_knowledge_context(session: Session, customer_id: uuid.UUID) -> str:
    statement = select(Document).where(
        Document.status == DocumentStatus.completed,
        Document.customer_id == customer_id,
    )
    documents = session.exec(statement).all()
    if not documents:
        return "No extracted document content is available yet."

    sections: list[str] = []
    for document in documents:
        extracted = document.extracted_data or {}
        summary = extracted.get("summary")
        if not summary:
            continue
        sections.append(f"### {document.title}\n{summary}")

    if not sections:
        return "No extracted document content is available yet."

    return "\n\n".join(sections)
