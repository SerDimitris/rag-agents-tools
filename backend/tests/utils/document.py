from sqlmodel import Session

from app import crud
from app.models import Document, DocumentCreate
from tests.utils.utils import random_lower_string


def create_random_document(db: Session) -> Document:
    title = random_lower_string()
    file_path = f"/uploads/{random_lower_string()}.pdf"
    document_in = DocumentCreate(title=title, file_path=file_path)
    return crud.create_document(session=db, document_in=document_in)
