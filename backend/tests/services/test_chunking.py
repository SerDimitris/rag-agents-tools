from app.services.chunking import chunk_document_text


GREEK_QA_DOCUMENT = """
Ερώτηση: Πώς μπορώ να μπλοκάρω την κάρτα μου σε περίπτωση απώλειας ή κλοπής;
Απάντηση: Καλέστε το 210 1234567 και επιλέξτε "Προσωρινή Δέσμευση".

Ερώτηση: Πώς αλλάζω το PIN;
Απάντηση: Μέσω της εφαρμογής, στο μενού "Κάρτες".
"""


def test_qa_pairs_stay_in_single_chunks() -> None:
    chunks = chunk_document_text(GREEK_QA_DOCUMENT)
    assert len(chunks) == 2
    assert chunks[0].chunk_type == "qa"
    assert "Ερώτηση:" in chunks[0].content
    assert "Απάντηση:" in chunks[0].content
    assert "απώλειας ή κλοπής" in chunks[0].content
    assert "Προσωρινή Δέσμευση" in chunks[0].content
    assert "PIN" in chunks[1].content


def test_generic_text_falls_back_to_paragraph_chunks() -> None:
    text = "Paragraph one about banking.\n\nParagraph two about cards."
    chunks = chunk_document_text(text)
    assert len(chunks) >= 1
    assert chunks[0].chunk_type == "text"
