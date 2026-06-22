from app.services.retriever import _keyword_score
from app.services.text_normalize import normalize_greek, tokenize_search_text, tokens_overlap


def test_normalize_greek_strips_accents() -> None:
    assert normalize_greek("κάρτα") == "καρτα"
    assert normalize_greek("Μπλοκάρισμα") == "μπλοκαρισμα"


def test_tokenize_search_text_ignores_short_tokens() -> None:
    assert tokenize_search_text("να το") == set()
    assert tokenize_search_text("κάρτα μου") == {"καρτα", "μου"}


def test_tokens_overlap_matches_greek_word_forms() -> None:
    assert tokens_overlap("μπλοκαρισμα", "μπλοκαρω")
    assert tokens_overlap("καρτας", "καρτα")


def test_keyword_score_matches_short_greek_card_query() -> None:
    content = (
        "Ερώτηση: Πώς μπορώ να μπλοκάρω την κάρτα μου;\n\n"
        "Απάντηση: Μπορείτε να μπλοκάρετε την κάρτα σας μέσω της Mobile App "
        "και «Προσωρινή Δέσμευση» ή στο +30 210 1234567."
    )
    score = _keyword_score("Μπλοκάρισμα καρτας.", content)
    assert score >= 0.5
