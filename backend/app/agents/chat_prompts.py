from app.models import CustomerSector
from app.services.text_normalize import tokenize_search_text

CHAT_GUIDELINES = """
Guidelines:
1. Intent Matching: Match the user's intent to the document knowledge. Users may ask using shorthand or different wording (e.g. "μπλόκο καρτα" maps to card loss/theft procedures).
2. Precision & Completeness: Do not omit phone numbers, system names, menu paths, or exact UI labels from the documents.
3. Grounding: Rely ONLY on facts in the Document knowledge below. Few-shot examples show format and tone, not facts to invent.
4. Fallback: If the context cannot answer the question, state clearly: "Δεν βρέθηκαν επαρκείς πληροφορίες στα έγγραφα για να απαντηθεί αυτό το ερώτημα."
5. Clarification: If the question is vague OR the retrieved document knowledge covers multiple distinct scenarios, ask 1-2 specific clarifying questions instead of guessing. Reference document topics you actually have (e.g. card loss vs PIN reset). Ask at most 2 questions. Do not invent options not supported by the retrieved context.
"""

SECTOR_PROFILES: dict[CustomerSector, str] = {
    CustomerSector.banking: """
Sector profile (Banking): You assist with cards, accounts, loans, transfers, PIN, fraud, and digital banking.
Tone: precise, security-aware, step-by-step. Preserve exact menu names (e.g. «Προσωρινή Δέσμευση») and phone numbers from the documents.
""",
    CustomerSector.telecom: """
Sector profile (Telecom): You assist with mobile/internet plans, SIM, billing, roaming, outages, routers, and Wi‑Fi.
Tone: practical troubleshooting with numbered steps (app, SMS codes, technician visit) using only document facts.
""",
    CustomerSector.energy: """
Sector profile (Energy): You assist with electricity/gas supply, bills, meter readings, outages, and tariff changes.
Tone: calm and explanatory. Clarify billing periods and kWh only when the documents mention them.
""",
    CustomerSector.general: """
Sector profile (General call center): You are a helpful internal support agent for any topic covered by the documents.
Tone: friendly, concise, procedural. Avoid sector jargon unless the documents use it.
""",
}

FEW_SHOT_EXAMPLES: dict[CustomerSector, list[dict[str, str]]] = {
    CustomerSector.banking: [
        {
            "role": "user",
            "content": "έχασα την κάρτα, τι κάνω;",
        },
        {
            "role": "assistant",
            "content": (
                "Σε περίπτωση απώλειας ή κλοπής κάρτας, ακολουθήστε μόνο τα βήματα από τα έγγραφα:\n"
                "1. Καλέστε τον αριθμό που αναφέρεται στα έγγραφα και επιλέξτε «Προσωρινή Δέσμευση» αν υπάρχει.\n"
                "2. Εναλλακτικά, μέσω της εφαρμογής: ακολουθήστε την ακριβή διαδρομή μενού από τα έγγραφα.\n"
                "Μην κοινοποιείτε τον PIN. Αν τα έγγραφα δεν περιέχουν αριθμό ή βήματα, δηλώστε ότι δεν βρέθηκαν επαρκείς πληροφορίες."
            ),
        },
    ],
    CustomerSector.telecom: [
        {
            "role": "user",
            "content": "δεν έχω internet στο σπίτι",
        },
        {
            "role": "assistant",
            "content": (
                "Για διακοπή internet, χρησιμοποιήστε μόνο τις οδηγίες από τα έγγραφα:\n"
                "1. Έλεγχος router / καλωδίων αν περιγράφεται.\n"
                "2. Επανεκκίνηση ή επανασύνδεση αν περιγράφεται.\n"
                "3. Αν το πρόβλημα παραμένει: τηλέφωνο υποστήριξης ή δήλωση βλάβης μόνο αν υπάρχει στα έγγραφα.\n"
                "Αναφέρετε κωδικούς SMS και ονόματα εφαρμογών μόνο όταν υπάρχουν στα έγγραφα."
            ),
        },
    ],
    CustomerSector.energy: [
        {
            "role": "user",
            "content": "γιατί ήρθε τόσο μεγάλος λογαριασμός;",
        },
        {
            "role": "assistant",
            "content": (
                "Για εξήγηση υψηλού λογαριαργού, χρησιμοποιήστε μόνο πληροφορίες από τα έγγραφα:\n"
                "• Περίοδος χρέωσης και κατανάλωση (kWh) αν αναφέρονται.\n"
                "• Τυχόν ρήτρες (εφεδρείο, ρυθμιζόμενη χρέωση) αν αναφέρονται.\n"
                "• Πώς ο πελάτης ζητά αναλυτική κατάσταση αν περιγράφεται.\n"
                "Αν τα έγγραφα δεν καλύπτουν την περίπτωση, δηλώστε ότι δεν βρέθηκαν επαρκείς πληροφορίες."
            ),
        },
    ],
    CustomerSector.general: [
        {
            "role": "user",
            "content": "πού μπορώ να βρω το αίτημα που έκανα;",
        },
        {
            "role": "assistant",
            "content": (
                "Βάσει των διαθέσιμων εγγραφών:\n"
                "1. Πού εμφανίζονται αιτήματα (portal, email, app) αν περιγράφεται.\n"
                "2. Τι χρειάζεται ο πελάτης (αριθμός αιτήματος, ID) αν περιγράφεται.\n"
                "3. Επόμενο βήμα αν δεν το βρίσκει, μόνο αν περιγράφεται.\n"
                "Αν τα έγγραφα δεν καλύπτουν το θέμα, ενημερώστε ευγενικά και προτείνετε γενική γραμμή μόνο αν υπάρχει στα έγγραφα."
            ),
        },
    ],
}

SECTOR_KEYWORD_HINTS: dict[CustomerSector, frozenset[str]] = {
    CustomerSector.banking: frozenset(
        {
            "καρτα",
            "καρτες",
            "pin",
            "τραπεζ",
            "λογαριασμος",
            "μπλοκ",
            "κλοπ",
            "απωλεια",
            "δανειο",
            "μεταφορα",
            "iban",
            "atm",
        }
    ),
    CustomerSector.telecom: frozenset(
        {
            "internet",
            "wifi",
            "router",
            "sim",
            "κινητο",
            "τηλεφωνο",
            "roaming",
            "συνδεση",
            "4g",
            "5g",
            "βλαβη",
            "οπτικο",
            "fiber",
        }
    ),
    CustomerSector.energy: frozenset(
        {
            "ρευμα",
            "ενεργεια",
            "kwh",
            "καυσιμο",
            "αεριο",
            "μετρητη",
            "καταναλωση",
            "τιμολογιο",
            "δεη",
            "προμηθευτη",
            "διακοπη",
            "ρευματος",
        }
    ),
    CustomerSector.general: frozenset(),
}

_OVERRIDE_MIN_SCORE = 2


def _score_sector_from_message(message: str, sector: CustomerSector) -> int:
    hints = SECTOR_KEYWORD_HINTS[sector]
    if not hints:
        return 0
    tokens = tokenize_search_text(message)
    return sum(1 for token in tokens if token in hints)


def resolve_effective_sector(
    customer_sector: CustomerSector,
    user_message: str,
) -> CustomerSector:
    customer_score = _score_sector_from_message(user_message, customer_sector)
    best_sector = customer_sector
    best_score = customer_score

    for sector in CustomerSector:
        if sector == CustomerSector.general:
            continue
        score = _score_sector_from_message(user_message, sector)
        if score > best_score:
            best_sector = sector
            best_score = score

    if (
        best_sector != customer_sector
        and best_score >= _OVERRIDE_MIN_SCORE
        and best_score > customer_score
    ):
        return best_sector
    return customer_sector


def build_system_prompt(
    knowledge: str,
    customer_sector: CustomerSector,
    effective_sector: CustomerSector,
) -> str:
    sector_note = ""
    if effective_sector != customer_sector:
        sector_note = (
            f"\nThis customer's primary sector is {customer_sector.value}. "
            f"The current question appears {effective_sector.value}-related; "
            f"use the {effective_sector.value} profile while staying grounded in the documents.\n"
        )

    return (
        "You are a precise and helpful assistant for an internal document knowledge base.\n\n"
        "Your core task is to answer based strictly on the Document knowledge below.\n"
        f"{sector_note}"
        f"{SECTOR_PROFILES[effective_sector].strip()}\n"
        f"{CHAT_GUIDELINES.strip()}\n\n"
        "Document knowledge:\n"
        f"{knowledge}"
    )


def few_shot_messages_for_sector(sector: CustomerSector) -> list[dict[str, str]]:
    return list(FEW_SHOT_EXAMPLES[sector])
