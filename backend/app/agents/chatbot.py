import logging
import uuid
from dataclasses import dataclass
from typing import Any, cast

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam
from sqlmodel import Session, col, select

from app.agents.chat_prompts import (
    build_system_prompt,
    few_shot_messages_for_sector,
    resolve_effective_sector,
)
from app.agents.extractor import build_knowledge_context
from app.agents.rag_confidence import (
    assess_retrieval_confidence,
    classify_response_kind,
)
from app.core.config import settings
from app.models import ChatMessage, Customer, CustomerSector
from app.services.llm import get_llm_client
from app.services.retriever import (
    RetrievalResult,
    RetrievedChunk,
    format_retrieved_context,
    retrieve_relevant_chunks,
)

logger = logging.getLogger(__name__)

LLM_UNAVAILABLE_MESSAGE = (
    "The AI model is temporarily unavailable, so I could not generate an answer. "
    "Please try again in a moment."
)


def _customer_sector(session: Session, customer_id: uuid.UUID) -> CustomerSector:
    customer = session.get(Customer, customer_id)
    if customer is None:
        return CustomerSector.general
    return customer.sector


@dataclass(frozen=True)
class ChatReply:
    content: str
    rag_trace: dict[str, Any] | None


@dataclass(frozen=True)
class PreparedChatReply:
    messages: list[ChatCompletionMessageParam] | None
    rag_trace: dict[str, Any] | None
    fallback: ChatReply | None


def build_rag_trace(
    chunks: list[RetrievedChunk],
    expanded_queries: list[str],
    *,
    used_fallback_context: bool,
    query: str,
    retrieval_mode: str = "none",
) -> dict[str, Any]:
    chunk_entries: list[dict[str, Any]] = []
    for rank, chunk in enumerate(chunks, start=1):
        chunk_entries.append(
            {
                "chunk_id": str(chunk.chunk_id),
                "document_id": str(chunk.document_id),
                "document_title": chunk.document_title,
                "score": round(chunk.score, 4),
                "rank": rank,
            }
        )

    max_score = max((chunk.score for chunk in chunks), default=None)
    confidence_fields = assess_retrieval_confidence(
        query,
        chunks,
        max_score=max_score,
    )
    return {
        "model": settings.OPENAI_MODEL,
        "top_k": settings.RAG_TOP_K,
        "expanded_queries": expanded_queries,
        "retrieval_mode": retrieval_mode,
        "chunks": chunk_entries,
        "max_score": round(max_score, 4) if max_score is not None else None,
        "used_fallback_context": used_fallback_context,
        **confidence_fields,
        "response_kind": "answer",
    }


def _resolve_knowledge(
    session: Session, user_message: str, customer_id: uuid.UUID
) -> tuple[str, RetrievalResult, bool]:
    retrieval = retrieve_relevant_chunks(session, user_message, customer_id)
    if retrieval.chunks:
        return format_retrieved_context(retrieval.chunks), retrieval, False

    # No chunk matched: fall back to the per-document LLM summaries.
    return build_knowledge_context(session, customer_id), retrieval, True


def _fallback_reply(
    user_message: str,
    knowledge: str,
    rag_trace: dict[str, Any],
) -> ChatReply:
    if knowledge.startswith("No extracted"):
        return ChatReply(
            content=(
                "I do not have any extracted document content yet. "
                "Please upload a document and wait for extraction to complete."
            ),
            rag_trace=rag_trace,
        )

    return ChatReply(
        content=(
            "The chat agent is running without an LLM configured. "
            f"Your question was: {user_message}\n\n"
            "Available knowledge preview:\n"
            f"{knowledge[:1500]}"
        ),
        rag_trace=rag_trace,
    )


def _build_chat_history(
    session: Session, user_id: uuid.UUID, customer_id: uuid.UUID
) -> list[ChatCompletionMessageParam]:
    statement = (
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .where(ChatMessage.customer_id == customer_id)
        .order_by(col(ChatMessage.created_at).desc())
        .limit(settings.RAG_CHAT_HISTORY_MESSAGES)
    )
    messages = list(reversed(session.exec(statement).all()))
    return cast(
        list[ChatCompletionMessageParam],
        [
            {"role": message.role.value, "content": message.content}
            for message in messages
        ],
    )


def _completion_content(
    client: OpenAI, messages: list[ChatCompletionMessageParam]
) -> str:
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=settings.RAG_LLM_MAX_TOKENS,
    )
    choice = response.choices[0]
    if choice.finish_reason == "length":
        logger.warning(
            "Chat completion hit RAG_LLM_MAX_TOKENS=%d; reply may be truncated",
            settings.RAG_LLM_MAX_TOKENS,
        )
    content = choice.message.content
    return content.strip() if content else ""


def prepare_chat_reply(
    session: Session,
    user_id: uuid.UUID,
    customer_id: uuid.UUID,
    user_message: str,
) -> PreparedChatReply:
    knowledge, retrieval, used_fallback = _resolve_knowledge(
        session, user_message, customer_id
    )
    rag_trace = build_rag_trace(
        retrieval.chunks,
        retrieval.expanded_queries,
        used_fallback_context=used_fallback,
        query=user_message,
        retrieval_mode=retrieval.mode,
    )

    client = get_llm_client()
    if client is None:
        return PreparedChatReply(
            messages=None,
            rag_trace=rag_trace,
            fallback=_fallback_reply(user_message, knowledge, rag_trace),
        )

    customer_sector = _customer_sector(session, customer_id)
    effective_sector = resolve_effective_sector(customer_sector, user_message)
    few_shots = few_shot_messages_for_sector(effective_sector)

    system_message = cast(
        ChatCompletionMessageParam,
        {
            "role": "system",
            "content": build_system_prompt(
                knowledge, customer_sector, effective_sector
            ),
        },
    )
    user_turn = cast(
        ChatCompletionMessageParam,
        {"role": "user", "content": user_message},
    )
    history = _build_chat_history(session, user_id, customer_id)
    messages: list[ChatCompletionMessageParam] = [
        system_message,
        *few_shots,
        *history,
        user_turn,
    ]

    return PreparedChatReply(messages=messages, rag_trace=rag_trace, fallback=None)


def _finalize_rag_trace(
    rag_trace: dict[str, Any] | None,
    content: str,
) -> dict[str, Any] | None:
    if rag_trace is None:
        return None

    finalized = dict(rag_trace)
    finalized["response_kind"] = classify_response_kind(
        content,
        clarification_recommended=bool(finalized.get("clarification_recommended")),
    )
    return finalized


def complete_chat_reply(prepared: PreparedChatReply) -> ChatReply:
    if prepared.fallback is not None:
        return ChatReply(
            content=prepared.fallback.content,
            rag_trace=_finalize_rag_trace(
                prepared.rag_trace, prepared.fallback.content
            ),
        )

    client = get_llm_client()
    if client is None:
        content = "I could not generate a response."
        return ChatReply(
            content=content,
            rag_trace=_finalize_rag_trace(prepared.rag_trace, content),
        )

    try:
        content = _completion_content(client, prepared.messages or [])
    except OpenAIError as exc:
        logger.exception("Chat completion failed")
        trace = _finalize_rag_trace(prepared.rag_trace, LLM_UNAVAILABLE_MESSAGE)
        if trace is not None:
            trace["llm_error"] = type(exc).__name__
        return ChatReply(content=LLM_UNAVAILABLE_MESSAGE, rag_trace=trace)

    final_content = content or "I could not generate a response."
    return ChatReply(
        content=final_content,
        rag_trace=_finalize_rag_trace(prepared.rag_trace, final_content),
    )


def generate_chat_reply(
    session: Session,
    user_id: uuid.UUID,
    customer_id: uuid.UUID,
    user_message: str,
) -> ChatReply:
    prepared = prepare_chat_reply(session, user_id, customer_id, user_message)
    return complete_chat_reply(prepared)
