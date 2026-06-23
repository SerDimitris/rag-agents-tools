import uuid
from io import BytesIO

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.customer import create_random_customer
from tests.utils.document import create_random_document


def test_create_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    data = {
        "title": "Annual Report",
        "file_path": "/uploads/annual-report.pdf",
        "customer_id": str(customer.id),
    }
    response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["file_path"] == data["file_path"]
    assert content["customer_id"] == str(customer.id)
    assert content["status"] == "pending"
    assert "id" in content


def test_upload_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    response = client.post(
        f"{settings.API_V1_STR}/documents/upload",
        headers=superuser_token_headers,
        files={"file": ("report.txt", BytesIO(b"Quarterly report content"), "text/plain")},
        data={"title": "Quarterly Report", "customer_id": str(customer.id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "Quarterly Report"
    assert content["status"] == "pending"
    assert content["customer_id"] == str(customer.id)
    assert content["file_path"].startswith(f"uploads/{customer.id}/")


def test_create_document_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    data = {
        "title": "Annual Report",
        "file_path": "/uploads/annual-report.pdf",
        "customer_id": str(customer.id),
    }
    response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    response = client.get(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
        params={"customer_id": str(document.customer_id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == document.title
    assert content["file_path"] == document.file_path
    assert content["id"] == str(document.id)
    assert content["status"] == document.status.value


def test_read_document_wrong_customer(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    other_customer = create_random_customer(db)
    response = client.get(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
        params={"customer_id": str(other_customer.id)},
    )
    assert response.status_code == 404


def test_read_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    response = client.get(
        f"{settings.API_V1_STR}/documents/{uuid.uuid4()}",
        headers=superuser_token_headers,
        params={"customer_id": str(customer.id)},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Document not found"


def test_read_document_as_viewer(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    response = client.get(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=normal_user_token_headers,
        params={"customer_id": str(document.customer_id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(document.id)


def test_read_documents_filtered_by_customer(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer_a = create_random_customer(db)
    customer_b = create_random_customer(db)
    create_random_document(db, customer_id=customer_a.id)
    create_random_document(db, customer_id=customer_a.id)
    create_random_document(db, customer_id=customer_b.id)

    response_a = client.get(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        params={"customer_id": str(customer_a.id)},
    )
    assert response_a.status_code == 200
    content_a = response_a.json()
    assert len(content_a["data"]) == 2
    assert all(item["customer_id"] == str(customer_a.id) for item in content_a["data"])

    response_b = client.get(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        params={"customer_id": str(customer_b.id)},
    )
    assert response_b.status_code == 200
    content_b = response_b.json()
    assert len(content_b["data"]) == 1
    assert content_b["data"][0]["customer_id"] == str(customer_b.id)


def test_update_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    data = {
        "title": "Updated title",
        "status": "completed",
        "extracted_data": {"pages": 12},
    }
    response = client.put(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
        params={"customer_id": str(document.customer_id)},
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["status"] == data["status"]
    assert content["extracted_data"] == data["extracted_data"]
    assert content["id"] == str(document.id)


def test_update_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    data = {"title": "Updated title", "status": "completed"}
    response = client.put(
        f"{settings.API_V1_STR}/documents/{uuid.uuid4()}",
        headers=superuser_token_headers,
        params={"customer_id": str(customer.id)},
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Document not found"


def test_update_document_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    data = {"title": "Updated title", "status": "completed"}
    response = client.put(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=normal_user_token_headers,
        params={"customer_id": str(document.customer_id)},
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_document(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    response = client.delete(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=superuser_token_headers,
        params={"customer_id": str(document.customer_id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Document deleted successfully"


def test_delete_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    customer = create_random_customer(db)
    response = client.delete(
        f"{settings.API_V1_STR}/documents/{uuid.uuid4()}",
        headers=superuser_token_headers,
        params={"customer_id": str(customer.id)},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Document not found"


def test_delete_document_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    document = create_random_document(db)
    response = client.delete(
        f"{settings.API_V1_STR}/documents/{document.id}",
        headers=normal_user_token_headers,
        params={"customer_id": str(document.customer_id)},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
