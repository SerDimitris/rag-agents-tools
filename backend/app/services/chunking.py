import re
from dataclasses import dataclass

from app.core.config import settings

QA_BLOCK_PATTERN = re.compile(
    r"(?:Ερώτηση|ερώτηση|Question)\s*[:\.]?\s*"
    r"(.*?)\s*"
    r"(?:Απάντηση|απάντηση|Answer)\s*[:\.]?\s*"
    r"(.*?)(?=(?:Ερώτηση|ερώτηση|Question)\s*[:\.]|\Z)",
    re.DOTALL | re.IGNORECASE,
)


@dataclass(frozen=True)
class TextChunk:
    content: str
    chunk_type: str
    chunk_index: int


def _format_qa_chunk(question: str, answer: str) -> str:
    question = question.strip()
    answer = answer.strip()
    return f"Ερώτηση: {question}\n\nΑπάντηση: {answer}"


def _split_generic_text(text: str) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""
    max_size = settings.RAG_CHUNK_SIZE
    overlap = settings.RAG_CHUNK_OVERLAP

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
            if overlap > 0 and len(current) > overlap:
                current = current[-overlap:].strip()
                current = f"{current}\n\n{paragraph}".strip()
            else:
                current = paragraph
        else:
            start = 0
            while start < len(paragraph):
                chunks.append(paragraph[start : start + max_size].strip())
                start += max(max_size - overlap, 1)
            current = ""

    if current:
        chunks.append(current)

    return chunks


def chunk_document_text(text: str) -> list[TextChunk]:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []

    qa_chunks: list[TextChunk] = []
    matched_spans: list[tuple[int, int]] = []

    for match in QA_BLOCK_PATTERN.finditer(normalized):
        question = match.group(1).strip()
        answer = match.group(2).strip()
        if not question or not answer:
            continue
        matched_spans.append((match.start(), match.end()))
        qa_chunks.append(
            TextChunk(
                content=_format_qa_chunk(question, answer),
                chunk_type="qa",
                chunk_index=len(qa_chunks),
            )
        )

    if qa_chunks:
        return qa_chunks

    generic_chunks = _split_generic_text(normalized)
    return [
        TextChunk(content=chunk, chunk_type="text", chunk_index=index)
        for index, chunk in enumerate(generic_chunks)
    ]
