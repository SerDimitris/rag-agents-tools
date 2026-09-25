from unittest.mock import MagicMock

import pytest

from app.services.query_expansion import _parse_variations, expand_query


def test_parse_variations_plain_json_array() -> None:
    assert _parse_variations('["α", "β"]') == ["α", "β"]


def test_parse_variations_json_with_trailing_text() -> None:
    assert _parse_variations('["χαμένη κάρτα", "μπλοκάρισμα κάρτας"];') == [
        "χαμένη κάρτα",
        "μπλοκάρισμα κάρτας",
    ]


def test_parse_variations_json_in_code_fence() -> None:
    raw = '```json\n["αλλαγή PIN", "νέος κωδικός PIN"]\n```'
    assert _parse_variations(raw) == ["αλλαγή PIN", "νέος κωδικός PIN"]


def test_parse_variations_numbered_lines_fallback() -> None:
    assert _parse_variations("1. πρώτο\n2) δεύτερο\n- τρίτο") == [
        "πρώτο",
        "δεύτερο",
        "τρίτο",
    ]


def test_expand_query_without_llm_returns_original(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.services.query_expansion.get_llm_client", lambda: None)
    assert expand_query("  έχασα την κάρτα  ") == ["έχασα την κάρτα"]


def test_expand_query_keeps_original_first_and_dedupes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices[
        0
    ].message.content = '["έχασα την κάρτα", "απώλεια κάρτας", "κλοπή κάρτας"]'
    monkeypatch.setattr(
        "app.services.query_expansion.get_llm_client", lambda: mock_client
    )

    assert expand_query("έχασα την κάρτα") == [
        "έχασα την κάρτα",
        "απώλεια κάρτας",
        "κλοπή κάρτας",
    ]
