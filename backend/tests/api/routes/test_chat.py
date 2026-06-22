from io import BytesIO

from fastapi.testclient import TestClient

from app.core.config import settings


def test_send_chat_message(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={"content": "What documents do you know about?"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["user_message"]["role"] == "user"
    assert content["assistant_message"]["role"] == "assistant"
    assert "document" in content["assistant_message"]["content"].lower()


def test_read_chat_messages(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
        json={"content": "Hello"},
    )
    response = client.get(
        f"{settings.API_V1_STR}/chat/messages",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
