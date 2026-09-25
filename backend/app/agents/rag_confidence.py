import re
from typing import Any, Literal

from app.core.config import settings
from app.services.retriever import RetrievedChunk
from app.services.text_normalize import normalize_greek, tokenize_search_text

ConfidenceLevel = Literal["low", "medium", "high"]
ResponseKind = Literal["answer", "clarification"]

_GREEK_LETTER = re.compile(r"[Ͱ-Ͽ]")
_TRAILING_DECORATION = " \t\n*_)»\"'"


def _question_marks(text: str) -> str:
    # Greek writes the question mark as ";" (its semicolon is "·"), so ";"
    # only counts in Greek text and English semicolons are not questions.
    if _GREEK_LETTER.search(text):
        # (normalize_greek applies NFD, which maps U+037E to a plain ";".)
        return "?;"
    return "?"


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


# Phrases that are an explicit request for clarification on their own, so the
# reply counts as a clarification even when retrieval did not recommend one.
EXPLICIT_CLARIFY_PHRASES = (
    "διευκριν",
    "clarif",
    "please specify",
    "which of",
    "ποιο απο",
)


def classify_response_kind(
    content: str,
    *,
    clarification_recommended: bool,
) -> ResponseKind:
    normalized = normalize_greek(content.strip())
    if not normalized:
        return "answer"

    marks = _question_marks(normalized)
    question_count = sum(normalized.count(mark) for mark in marks)
    if not question_count:
        return "answer"

    if not clarification_recommended:
        explicit = any(phrase in normalized for phrase in EXPLICIT_CLARIFY_PHRASES)
        return "clarification" if explicit else "answer"

    has_clarify_phrase = any(
        normalize_greek(phrase) in normalized for phrase in CLARIFY_PHRASES
    )
    ends_with_question = normalized.rstrip(_TRAILING_DECORATION)[-1:] in marks
    if has_clarify_phrase or ends_with_question or question_count >= 2:
        return "clarification"

    return "answer"
