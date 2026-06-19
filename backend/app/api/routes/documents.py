import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep, get_current_moderator
from app.models import (
    Document,
    DocumentCreate,
    DocumentPublic,
    DocumentsPublic,
    DocumentUpdate,
    Message,
    User,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=DocumentsPublic)
def read_documents(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve documents.
    """
    count_statement = select(func.count()).select_from(Document)
    count = session.exec(count_statement).one()
    statement = (
        select(Document)
        .order_by(col(Document.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    documents = session.exec(statement).all()

    documents_public = [
        DocumentPublic.model_validate(document) for document in documents
    ]
    return DocumentsPublic(data=documents_public, count=count)


@router.get("/{id}", response_model=DocumentPublic)
def read_document(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get document by ID.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/", response_model=DocumentPublic)
def create_document(
    *,
    session: SessionDep,
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_moderator),
) -> Any:
    """
    Create new document.
    """
    document = Document.model_validate(document_in)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.put("/{id}", response_model=DocumentPublic)
def update_document(
    *,
    session: SessionDep,
    id: uuid.UUID,
    current_user: User = Depends(get_current_moderator),
    document_in: DocumentUpdate,
) -> Any:
    """
    Update a document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    update_dict = document_in.model_dump(exclude_unset=True)
    document.sqlmodel_update(update_dict)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/{id}")
def delete_document(
    session: SessionDep,
    id: uuid.UUID,
    current_user: User = Depends(get_current_moderator),
) -> Message:
    """
    Delete a document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    session.delete(document)
    session.commit()
    return Message(message="Document deleted successfully")
