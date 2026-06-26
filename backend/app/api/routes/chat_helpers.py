import uuid
from typing import Any

from app.models import (
    ChatMessage,
    ChatMessagePublic,
    ChatResponseKind,
    MessageFeedback,
)


def source_titles_from_rag_trace(rag_trace: dict[str, Any] | None) -> list[str]:
    if not rag_trace:
        return []

    titles: list[str] = []
    seen: set[str] = set()
    for chunk in rag_trace.get("chunks", []):
        title = chunk.get("document_title")
        if isinstance(title, str) and title and title not in seen:
            seen.add(title)
            titles.append(title)
    return titles


def response_kind_from_rag_trace(rag_trace: dict[str, Any] | None) -> ChatResponseKind:
    if not rag_trace:
        return ChatResponseKind.answer

    raw_kind = rag_trace.get("response_kind")
    if raw_kind == ChatResponseKind.clarification.value:
        return ChatResponseKind.clarification
    return ChatResponseKind.answer


def to_chat_message_public(
    message: ChatMessage,
    feedback: MessageFeedback | None = None,
) -> ChatMessagePublic:
    return ChatMessagePublic(
        id=message.id,
        content=message.content,
        customer_id=message.customer_id,
        role=message.role,
        reply_to_id=message.reply_to_id,
        source_titles=source_titles_from_rag_trace(message.rag_trace),
        response_kind=response_kind_from_rag_trace(message.rag_trace),
        feedback_rating=feedback.rating if feedback else None,
        created_at=message.created_at,
    )

def feedback_by_message_id(
    feedback_rows: list[MessageFeedback],
) -> dict[uuid.UUID, MessageFeedback]:
    return {row.message_id: row for row in feedback_rows}
