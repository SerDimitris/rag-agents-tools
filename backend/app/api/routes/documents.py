import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, col, func, select

from app.agents.extractor import run_document_extraction
from app.api.deps import CurrentUser, SessionDep, get_current_moderator
from app.core.config import settings
from app.core.db import engine
from app.models import (
    Document,
    DocumentCreate,
    DocumentPublic,
    DocumentsPublic,
    DocumentStatus,
    DocumentUpdate,
    Message,
    User,
)
from app.services.file_storage import delete_stored_file, get_upload_dir
from app.services.file_text import is_allowed_file

router = APIRouter(prefix="/documents", tags=["documents"])


def _schedule_extraction(background_tasks: BackgroundTasks, document_id: uuid.UUID) -> None:
    def _run() -> None:
        with Session(engine) as session:
            run_document_extraction(session, document_id)

    background_tasks.add_task(_run)


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


@router.post("/upload", response_model=DocumentPublic)
async def upload_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
) -> Any:
    """
    Upload a document file and start background extraction.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: .txt, .md, .pdf, .csv, .json",
        )

    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    document_id = uuid.uuid4()
    safe_name = Path(file.filename).name
    stored_name = f"{document_id}_{safe_name}"
    upload_dir = get_upload_dir()
    stored_path = upload_dir / stored_name
    stored_path.write_bytes(contents)

    document = Document(
        id=document_id,
        title=title or Path(safe_name).stem,
        file_path=f"uploads/{stored_name}",
        status=DocumentStatus.pending,
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    _schedule_extraction(background_tasks, document.id)
    return document


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
    Create new document metadata entry.
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


@router.post("/{id}/reextract", response_model=DocumentPublic)
def reextract_document(
    *,
    session: SessionDep,
    id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_moderator),
) -> Any:
    """
    Re-run LLM extraction for an existing document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = DocumentStatus.pending
    document.extracted_data = None
    session.add(document)
    session.commit()
    session.refresh(document)

    _schedule_extraction(background_tasks, document.id)
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
    delete_stored_file(document.file_path)
    session.delete(document)
    session.commit()
    return Message(message="Document deleted successfully")
