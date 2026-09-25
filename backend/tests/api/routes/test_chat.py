import uuid
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APIConnectionError
from sqlmodel import Session

from app.agents.chatbot import LLM_UNAVAILABLE_MESSAGE
from app.core.config import settings
from app.models import ChatMessage, Document, DocumentStatus
from app.services.retriever import index_document_chunks
from tests.utils.customer import create_random_customer


def test_send_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    response = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={
            "content": "What documents do you know about?",
            "customer_id": str(customer.id),
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content["user_message"]["role"] == "user"
    assert content["assistant_message"]["role"] == "assistant"
    assert content["user_message"]["customer_id"] == str(customer.id)
    assert content["assistant_message"]["reply_to_id"] == content["user_message"]["id"]
    assistant_text = content["assistant_message"]["content"].lower()
    assert "document" in assistant_text or "έγγραφ" in assistant_text


def test_send_chat_message_survives_llm_outage(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    customer = create_random_customer(db)
    document = Document(
        customer_id=customer.id,
        title="Card FAQ",
        file_path=f"uploads/{customer.id}/faq.txt",
        status=DocumentStatus.completed,
    )
    db.add(document)
    db.commit()
    index_document_chunks(
        db,
        document.id,
        "Question: How do I block my card?\nAnswer: Call 210 1234567.",
    )

    failing_client = MagicMock()
    failing_client.chat.completions.create.side_effect = APIConnectionError(
        request=httpx.Request("POST", "http://llm.test/v1/chat/completions")
    )
    monkeypatch.setattr("app.agents.chatbot.get_llm_client", lambda: failing_client)

    response = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={"content": "How do I block my card?", "customer_id": str(customer.id)},
    )

    assert response.status_code == 200
    assistant = response.json()["assistant_message"]
    assert assistant["content"] == LLM_UNAVAILABLE_MESSAGE
    assert assistant["source_titles"] == ["Card FAQ"]

    stored = db.get(ChatMessage, uuid.UUID(assistant["id"]))
    assert stored is not None and stored.rag_trace is not None
    assert stored.rag_trace["llm_error"] == "APIConnectionError"
    assert stored.rag_trace["retrieval_mode"] == "keyword"


def test_submit_message_feedback(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    chat_response = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={"content": "Hello", "customer_id": str(customer.id)},
    )
    assistant_message_id = chat_response.json()["assistant_message"]["id"]

    response = client.post(
        f"{settings.API_V1_STR}/chat/messages/{assistant_message_id}/feedback",
        headers=superuser_token_headers,
        json={"rating": "positive"},
    )
    assert response.status_code == 200
    assert response.json()["rating"] == "positive"
    assert response.json()["message_id"] == assistant_message_id

    messages_response = client.get(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        params={"customer_id": str(customer.id)},
    )
    assistant_messages = [
        item for item in messages_response.json()["data"] if item["role"] == "assistant"
    ]
    assert assistant_messages[-1]["feedback_rating"] == "positive"

    update_response = client.post(
        f"{settings.API_V1_STR}/chat/messages/{assistant_message_id}/feedback",
        headers=superuser_token_headers,
        json={"rating": "negative", "reason": "wrong"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["rating"] == "negative"
    assert update_response.json()["reason"] == "wrong"


def test_feedback_rejected_for_user_messages(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    chat_response = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={"content": "Hello", "customer_id": str(customer.id)},
    )
    user_message_id = chat_response.json()["user_message"]["id"]

    response = client.post(
        f"{settings.API_V1_STR}/chat/messages/{user_message_id}/feedback",
        headers=superuser_token_headers,
        json={"rating": "positive"},
    )
    assert response.status_code == 400


def test_read_chat_messages(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={"content": "Hello", "customer_id": str(customer.id)},
    )
    response = client.get(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        params={"customer_id": str(customer.id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2


def test_chat_messages_isolated_by_customer(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer_a = create_random_customer(db)
    customer_b = create_random_customer(db)

    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={"content": "Message for A", "customer_id": str(customer_a.id)},
    )
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={"content": "Message for B", "customer_id": str(customer_b.id)},
    )

    response_a = client.get(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        params={"customer_id": str(customer_a.id)},
    )
    response_b = client.get(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        params={"customer_id": str(customer_b.id)},
    )

    messages_a = [item["content"] for item in response_a.json()["data"]]
    messages_b = [item["content"] for item in response_b.json()["data"]]

    assert any("Message for A" in message for message in messages_a)
    assert not any("Message for A" in message for message in messages_b)
    assert any("Message for B" in message for message in messages_b)
    assert not any("Message for B" in message for message in messages_a)
