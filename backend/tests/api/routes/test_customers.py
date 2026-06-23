from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.customer import create_random_customer


def test_read_customers(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_customer(db)
    create_random_customer(db)
    response = client.get(
        f"{settings.API_V1_STR}/customers/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_create_customer(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/customers/",
        headers=superuser_token_headers,
        json={"name": "Acme Corp", "description": "Test customer"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == "Acme Corp"
    assert content["description"] == "Test customer"
    assert content["is_active"] is True


def test_create_customer_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/customers/",
        headers=normal_user_token_headers,
        json={"name": "Forbidden Customer"},
    )
    assert response.status_code == 403


def test_update_customer(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    response = client.put(
        f"{settings.API_V1_STR}/customers/{customer.id}",
        headers=superuser_token_headers,
        json={"name": "Updated Name", "is_active": False},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == "Updated Name"
    assert content["is_active"] is False


def test_delete_customer(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    response = client.delete(
        f"{settings.API_V1_STR}/customers/{customer.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted successfully"
