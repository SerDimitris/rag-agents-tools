import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.document import create_random_document


def test_create_document(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Annual Report", "file_path": "/uploads/annual-report.pdf"}
    response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["file_path"] == data["file_path"]
    assert content["status"] == "pending"
    assert "id" in content


def test_create_document_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {"title": "Annual Report", "file_path": "/uploads/annual-report.pdf"}
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
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == document.title
    assert content["file_path"] == document.file_path
    assert content["id"] == str(document.id)
    assert content["status"] == document.status.value


def test_read_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/documents/{uuid.uuid4()}",
        headers=superuser_token_headers,
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
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(document.id)


def test_read_documents(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_document(db)
    create_random_document(db)
    response = client.get(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


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
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["status"] == data["status"]
    assert content["extracted_data"] == data["extracted_data"]
    assert content["id"] == str(document.id)


def test_update_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "status": "completed"}
    response = client.put(
        f"{settings.API_V1_STR}/documents/{uuid.uuid4()}",
        headers=superuser_token_headers,
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
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Document deleted successfully"


def test_delete_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/documents/{uuid.uuid4()}",
        headers=superuser_token_headers,
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
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
