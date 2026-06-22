import re
import unicodedata

GREEK_ACCENT_MAP = str.maketrans(
    {
        "ά": "α",
        "έ": "ε",
        "ή": "η",
        "ί": "ι",
        "ό": "ο",
        "ύ": "υ",
        "ώ": "ω",
        "ϊ": "ι",
        "ΐ": "ι",
        "ϋ": "υ",
        "ΰ": "υ",
        "Ά": "α",
        "Έ": "ε",
        "Ή": "η",
        "Ί": "ι",
        "Ό": "ο",
        "Ύ": "υ",
        "Ώ": "ω",
    }
)


def normalize_greek(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    stripped = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return stripped.translate(GREEK_ACCENT_MAP).lower()


def tokenize_search_text(text: str) -> set[str]:
    normalized = normalize_greek(text)
    return {
        token
        for token in re.findall(r"[\w\u0370-\u03FF]+", normalized)
        if len(token) >= 3
    }


def tokens_overlap(query_token: str, content_token: str) -> bool:
    if query_token == content_token:
        return True
    if len(query_token) < 4 or len(content_token) < 4:
        return False
    prefix_len = min(len(query_token), len(content_token), 5)
    return query_token[:prefix_len] == content_token[:prefix_len]
