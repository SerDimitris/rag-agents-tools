import json
import re

from app.core.config import settings
from app.services.llm import get_llm_client

QUERY_EXPANSION_PROMPT = """You expand short user questions for semantic document search.

Given a user question (often in Greek), produce exactly {count} alternative search queries that:
- preserve the same intent
- add related concepts, synonyms, and common longer phrasing
- stay in Greek when the input is Greek

Return ONLY a JSON array of strings. No markdown, no explanation.

User question:
{query}
"""


def _parse_variations(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass

    lines = [line.strip(" -\t") for line in raw.splitlines() if line.strip()]
    cleaned: list[str] = []
    for line in lines:
        line = re.sub(r"^\d+[\).\s]+", "", line).strip()
        if line:
            cleaned.append(line)
    return cleaned


def _is_short_query(query: str) -> bool:
    words = [word for word in query.split() if word.strip()]
    return len(words) <= settings.RAG_SHORT_QUERY_WORDS


def expand_query(query: str, *, variation_count: int | None = None) -> list[str]:
    query = query.strip()
    if not query:
        return []

    if _is_short_query(query):
        variation_count = max(
            variation_count or settings.RAG_QUERY_EXPANSION_COUNT,
            settings.RAG_QUERY_EXPANSION_COUNT + 2,
        )
    else:
        variation_count = variation_count or settings.RAG_QUERY_EXPANSION_COUNT

    client = get_llm_client()
    if client is None:
        return [query]

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": QUERY_EXPANSION_PROMPT.format(
                        count=variation_count,
                        query=query,
                    ),
                }
            ],
            temperature=0.3,
            max_tokens=512,
        )
    except Exception:  # noqa: BLE001
        return [query]

    content = response.choices[0].message.content or ""
    variations = _parse_variations(content)
    unique: list[str] = [query]
    for variation in variations:
        if variation not in unique:
            unique.append(variation)
        if len(unique) >= variation_count + 1:
            break
    return unique[: variation_count + 1]
