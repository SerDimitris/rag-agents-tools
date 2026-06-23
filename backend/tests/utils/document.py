import uuid

from sqlmodel import Session

from app import crud
from app.models import Document, DocumentCreate
from tests.utils.utils import random_lower_string


def create_random_document(db: Session, customer_id: uuid.UUID | None = None) -> Document:
    from tests.utils.customer import create_random_customer

    if customer_id is None:
        customer_id = create_random_customer(db).id

    title = random_lower_string()
    file_path = f"/uploads/{customer_id}/{random_lower_string()}.pdf"
    document_in = DocumentCreate(
        title=title, file_path=file_path, customer_id=customer_id
    )
    return crud.create_document(session=db, document_in=document_in)
