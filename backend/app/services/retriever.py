import uuid
from dataclasses import dataclass

from sqlalchemy import delete
from sqlmodel import Session, col, select

from app.core.config import settings
from app.models import Document, DocumentChunk, DocumentStatus
from app.services.chunking import chunk_document_text
from app.services.embeddings import create_embeddings
from app.services.query_expansion import expand_query
from app.services.text_normalize import tokenize_search_text, tokens_overlap


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    content: str
    score: float


def index_document_chunks(
    session: Session, document_id: uuid.UUID, raw_text: str
) -> int:
    session.exec(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

    chunks = chunk_document_text(raw_text)
    if not chunks:
        return 0

    embeddings = create_embeddings([chunk.content for chunk in chunks])
    for chunk, embedding in zip(chunks, embeddings, strict=True):
        session.add(
            DocumentChunk(
                document_id=document_id,
                chunk_index=chunk.chunk_index,
                chunk_type=chunk.chunk_type,
                content=chunk.content,
                embedding=embedding,
            )
        )
    session.commit()
    return len(chunks)


def _keyword_score(query: str, content: str) -> float:
    query_tokens = tokenize_search_text(query)
    if not query_tokens:
        return 0.0
    content_tokens = tokenize_search_text(content)
    if not content_tokens:
        return 0.0

    matched = 0
    for query_token in query_tokens:
        if any(tokens_overlap(query_token, content_token) for content_token in content_tokens):
            matched += 1
    return matched / len(query_tokens)


def _search_by_embedding(
    session: Session, query_embedding: list[float], *, limit: int
) -> list[RetrievedChunk]:
    distance_expr = DocumentChunk.embedding.cosine_distance(query_embedding)
    statement = (
        select(
            DocumentChunk,
            Document.title,
            distance_expr.label("distance"),
        )
        .join(Document, col(Document.id) == col(DocumentChunk.document_id))
        .where(Document.status == DocumentStatus.completed)
        .where(col(DocumentChunk.embedding).is_not(None))
        .order_by(distance_expr)
        .limit(limit)
    )
    rows = session.exec(statement).all()
    results: list[RetrievedChunk] = []
    for chunk, title, distance in rows:
        results.append(
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_title=title,
                content=chunk.content,
                score=1.0 - float(distance),
            )
        )
    return results


def _search_by_keywords(
    session: Session, query: str, *, limit: int
) -> list[RetrievedChunk]:
    statement = (
        select(DocumentChunk, Document.title)
        .join(Document, col(Document.id) == col(DocumentChunk.document_id))
        .where(Document.status == DocumentStatus.completed)
    )
    rows = session.exec(statement).all()
    scored: list[RetrievedChunk] = []
    for chunk, title in rows:
        score = _keyword_score(query, chunk.content)
        if score <= 0:
            continue
        scored.append(
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_title=title,
                content=chunk.content,
                score=score,
            )
        )
    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]


def retrieve_relevant_chunks(
    session: Session, query: str, *, top_k: int | None = None
) -> list[RetrievedChunk]:
    top_k = top_k or settings.RAG_TOP_K
    expanded_queries = expand_query(query)
    merged: dict[uuid.UUID, RetrievedChunk] = {}

    embeddings = create_embeddings(expanded_queries)
    has_embeddings = any(embedding is not None for embedding in embeddings)

    if has_embeddings:
        per_query_limit = max(top_k, 3)
        for expanded_query, query_embedding in zip(
            expanded_queries, embeddings, strict=True
        ):
            if query_embedding is None:
                continue
            for result in _search_by_embedding(
                session, query_embedding, limit=per_query_limit
            ):
                existing = merged.get(result.chunk_id)
                if existing is None or result.score > existing.score:
                    merged[result.chunk_id] = result

    if not merged:
        for expanded_query in expanded_queries:
            for result in _search_by_keywords(session, expanded_query, limit=top_k):
                existing = merged.get(result.chunk_id)
                if existing is None or result.score > existing.score:
                    merged[result.chunk_id] = result

    ranked = sorted(merged.values(), key=lambda item: item.score, reverse=True)
    return ranked[:top_k]


def format_retrieved_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "No extracted document content is available yet."

    sections: list[str] = []
    for chunk in chunks:
        sections.append(f"### {chunk.document_title}\n{chunk.content}")
    return "\n\n".join(sections)


def retrieve_knowledge_context(session: Session, query: str) -> str:
    chunks = retrieve_relevant_chunks(session, query)
    return format_retrieved_context(chunks)
