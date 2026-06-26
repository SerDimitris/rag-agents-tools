from typing import Any, Literal

from app.core.config import settings
from app.services.retriever import RetrievedChunk
from app.services.text_normalize import tokenize_search_text

ConfidenceLevel = Literal["low", "medium", "high"]
ResponseKind = Literal["answer", "clarification"]

CLARIFY_PHRASES = (
    "διευκρίν",
    "clarif",
    "which of",
    "ποιο από",
    "μπορείτε να",
    "please specify",
    "could you tell",
    "need a bit more",
    "παρακαλώ διευκριν",
)


def assess_retrieval_confidence(
    query: str,
    chunks: list[RetrievedChunk],
    *,
    max_score: float | None,
) -> dict[str, Any]:
    triggers: list[str] = []

    if not chunks:
        triggers.append("no_chunks")

    if max_score is None or max_score < settings.RAG_MIN_SCORE_FOR_ANSWER:
        if chunks:
            triggers.append("low_retrieval_score")

    if len(chunks) >= 2:
        top_chunks = chunks[:3]
        document_ids = {chunk.document_id for chunk in top_chunks}
        top_scores = [chunk.score for chunk in top_chunks]
        if len(document_ids) >= 2 and len(top_scores) >= 2:
            score_spread = top_scores[0] - top_scores[-1]
            if score_spread <= settings.RAG_MULTI_DOC_SCORE_SPREAD:
                triggers.append("multi_document_ambiguity")

    query_tokens = tokenize_search_text(query)
    short_query_threshold = max_score is None or max_score < (
        settings.RAG_MIN_SCORE_FOR_ANSWER + 0.1
    )
    if (
        len(query_tokens) <= settings.RAG_SHORT_QUERY_WORDS
        and chunks
        and short_query_threshold
    ):
        triggers.append("short_vague_query")

    if "no_chunks" in triggers or (
        "low_retrieval_score" in triggers and len(triggers) == 1
    ):
        confidence: ConfidenceLevel = "low"
    elif triggers:
        confidence = "medium"
    else:
        confidence = "high"

    clarification_recommended = bool(chunks) and any(
        trigger != "no_chunks" for trigger in triggers
    )

    return {
        "confidence": confidence,
        "clarification_triggers": triggers,
        "clarification_recommended": clarification_recommended,
    }


def classify_response_kind(
    content: str,
    *,
    clarification_recommended: bool,
) -> ResponseKind:
    stripped = content.strip()
    if not stripped or not clarification_recommended:
        return "answer"

    lower = stripped.lower()
    has_question = "?" in stripped
    has_clarify_phrase = any(phrase in lower for phrase in CLARIFY_PHRASES)

    if has_question and (has_clarify_phrase or stripped.endswith("?")):
        return "clarification"

    if stripped.count("?") >= 2:
        return "clarification"

    return "answer"
