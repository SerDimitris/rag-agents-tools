from app.agents.chat_prompts import (
    build_system_prompt,
    few_shot_messages_for_sector,
    resolve_effective_sector,
)
from app.models import CustomerSector


def test_resolve_effective_sector_uses_customer_default() -> None:
    sector = resolve_effective_sector(CustomerSector.banking, "γεια σας")
    assert sector == CustomerSector.banking


def test_resolve_effective_sector_overrides_on_strong_telecom_signal() -> None:
    sector = resolve_effective_sector(
        CustomerSector.banking,
        "δεν έχω internet και το wifi router δεν πιάνει σήμα",
    )
    assert sector == CustomerSector.telecom


def test_resolve_effective_sector_keeps_customer_on_weak_cross_signal() -> None:
    sector = resolve_effective_sector(
        CustomerSector.banking,
        "ρωτάω για τον λογαριασμό μου",
    )
    assert sector == CustomerSector.banking


def test_few_shot_messages_for_sector_returns_user_assistant_pair() -> None:
    messages = few_shot_messages_for_sector(CustomerSector.energy)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_build_system_prompt_includes_sector_and_knowledge() -> None:
    prompt = build_system_prompt(
        "Sample knowledge chunk.",
        CustomerSector.banking,
        CustomerSector.banking,
    )
    assert "Banking" in prompt
    assert "Sample knowledge chunk." in prompt
    assert "Clarification" in prompt


def test_build_system_prompt_notes_sector_override() -> None:
    prompt = build_system_prompt(
        "Sample knowledge chunk.",
        CustomerSector.banking,
        CustomerSector.telecom,
    )
    assert "primary sector is banking" in prompt
    assert "telecom-related" in prompt
