from io import BytesIO

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
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
    assert "document" in content["assistant_message"]["content"].lower()


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
