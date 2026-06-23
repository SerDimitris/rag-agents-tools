import uuid

from openai import OpenAI
from sqlmodel import Session, col, select

from app.agents.extractor import build_knowledge_context
from app.core.config import settings
from app.models import ChatMessage, ChatMessageRole
from app.services.llm import get_llm_client
from app.services.retriever import retrieve_knowledge_context

CHAT_SYSTEM_PROMPT = """You are a precise and helpful assistant for an internal document knowledge base.

Your core task is to answer the user's questions based strictly on the provided "Document knowledge" context below.

Guidelines:
1. Intent Matching: Match the user's intent to the document knowledge. Users may ask questions using shorthand, partial phrases, or different wording (e.g., "how to block my card" maps to procedures for card loss/theft).
2. Precision & Completeness: Do not simplify or omit critical technical details, phone numbers, system names, or exact UI steps (e.g., specific button names like "Προσωρινή Δέσμευση").
3. Grounding: Rely ONLY on the clear facts directly mentioned in the context. Do not assume or extrapolate.
4. Fallback: If the context does not contain the answer or the intent cannot be reasonably matched, state clearly: "Δεν βρέθηκαν επαρκείς πληροφορίες στα έγγραφα για να απαντηθεί αυτό το ερώτημα."

Document knowledge:
{knowledge}
"""


def _fallback_reply(
    session: Session, user_message: str, customer_id: uuid.UUID
) -> str:
    knowledge = retrieve_knowledge_context(session, user_message, customer_id)
    if knowledge.startswith("No extracted"):
        knowledge = build_knowledge_context(session, customer_id)
    if knowledge.startswith("No extracted"):
        return (
            "I do not have any extracted document content yet. "
            "Please upload a document and wait for extraction to complete."
        )
    return (
        "The chat agent is running without an LLM configured. "
        f"Your question was: {user_message}\n\n"
        "Available knowledge preview:\n"
        f"{knowledge[:1500]}"
    )


def _build_chat_history(
    session: Session, user_id: uuid.UUID, customer_id: uuid.UUID
) -> list[dict[str, str]]:
    statement = (
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .where(ChatMessage.customer_id == customer_id)
        .order_by(col(ChatMessage.created_at).desc())
        .limit(settings.RAG_CHAT_HISTORY_MESSAGES)
    )
    messages = list(reversed(session.exec(statement).all()))
    return [{"role": message.role.value, "content": message.content} for message in messages]


def _completion_content(client: OpenAI, messages: list[dict[str, str]]) -> str:
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=settings.chat_max_tokens,
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""


def generate_chat_reply(
    session: Session,
    user_id: uuid.UUID,
    customer_id: uuid.UUID,
    user_message: str,
) -> str:
    client = get_llm_client()
    knowledge = retrieve_knowledge_context(session, user_message, customer_id)
    if knowledge.startswith("No extracted"):
        knowledge = build_knowledge_context(session, customer_id)

    if client is None:
        return _fallback_reply(session, user_message, customer_id)

    system_message = {
        "role": "system",
        "content": CHAT_SYSTEM_PROMPT.format(knowledge=knowledge),
    }
    user_turn = {"role": "user", "content": user_message}
    history = _build_chat_history(session, user_id, customer_id)

    attempts: list[list[dict[str, str]]] = [
        [system_message, user_turn],
        [system_message, *history, user_turn],
    ]

    best_reply = ""
    for messages in attempts:
        reply = _completion_content(client, messages)
        if len(reply) > len(best_reply):
            best_reply = reply

    return best_reply or "I could not generate a response."
