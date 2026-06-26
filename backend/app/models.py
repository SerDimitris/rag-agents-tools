import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import EmailStr
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.core.config import settings


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    viewer = "viewer"
    moderator = "moderator"


class DocumentStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class CustomerSector(str, Enum):
    banking = "banking"
    telecom = "telecom"
    energy = "energy"
    general = "general"


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.viewer)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class CustomerBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    sector: CustomerSector = Field(default=CustomerSector.general)
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    sector: CustomerSector | None = None
    is_active: bool | None = None


class Customer(CustomerBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class CustomerPublic(CustomerBase):
    id: uuid.UUID
    created_at: datetime | None = None


class CustomersPublic(SQLModel):
    data: list[CustomerPublic]
    count: int


# Shared properties
class DocumentBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)


# Properties to receive on document creation
class DocumentCreate(DocumentBase):
    file_path: str = Field(max_length=1024)
    customer_id: uuid.UUID


# Properties to receive on document update
class DocumentUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: DocumentStatus | None = None
    file_path: str | None = Field(default=None, max_length=1024)
    extracted_data: dict[str, Any] | None = None


# Database model, database table inferred from class name
class Document(DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_id: uuid.UUID = Field(
        foreign_key="customer.id", nullable=False, index=True, ondelete="RESTRICT"
    )
    status: DocumentStatus = Field(default=DocumentStatus.pending)
    file_path: str = Field(max_length=1024)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    extracted_data: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )


# Properties to return via API, id is always required
class DocumentPublic(DocumentBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    status: DocumentStatus
    file_path: str
    created_at: datetime | None = None
    extracted_data: dict[str, Any] | None = None


class DocumentsPublic(SQLModel):
    data: list[DocumentPublic]
    count: int


class DocumentChunk(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(
        foreign_key="document.id", nullable=False, ondelete="CASCADE"
    )
    chunk_index: int = Field(default=0)
    chunk_type: str = Field(default="text", max_length=32)
    content: str = Field(sa_column=Column(Text, nullable=False))
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=True),
    )


class ChatMessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class FeedbackRating(str, Enum):
    positive = "positive"
    negative = "negative"


class FeedbackReason(str, Enum):
    wrong = "wrong"
    incomplete = "incomplete"
    outdated = "outdated"
    off_topic = "off_topic"
    other = "other"


class ChatResponseKind(str, Enum):
    answer = "answer"
    clarification = "clarification"


class ChatMessageBase(SQLModel):
    content: str = Field(min_length=1, max_length=10000)


class ChatMessageCreate(ChatMessageBase):
    customer_id: uuid.UUID


class ChatMessage(ChatMessageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    customer_id: uuid.UUID = Field(
        foreign_key="customer.id", nullable=False, index=True, ondelete="CASCADE"
    )
    role: ChatMessageRole
    reply_to_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="chatmessage.id",
        nullable=True,
        index=True,
    )
    rag_trace: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class ChatMessagePublic(ChatMessageBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    role: ChatMessageRole
    reply_to_id: uuid.UUID | None = None
    source_titles: list[str] = Field(default_factory=list)
    response_kind: ChatResponseKind = ChatResponseKind.answer
    feedback_rating: FeedbackRating | None = None
    created_at: datetime | None = None


class ChatMessagesPublic(SQLModel):
    data: list[ChatMessagePublic]
    count: int


class ChatResponse(SQLModel):
    user_message: ChatMessagePublic
    assistant_message: ChatMessagePublic


class MessageFeedbackCreate(SQLModel):
    rating: FeedbackRating
    reason: FeedbackReason | None = None
    comment: str | None = Field(default=None, max_length=2000)


class MessageFeedback(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID = Field(
        foreign_key="chatmessage.id",
        nullable=False,
        index=True,
        ondelete="CASCADE",
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    rating: FeedbackRating
    reason: FeedbackReason | None = None
    comment: str | None = Field(default=None, max_length=2000)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class MessageFeedbackPublic(SQLModel):
    id: uuid.UUID
    message_id: uuid.UUID
    rating: FeedbackRating
    reason: FeedbackReason | None = None
    comment: str | None = None
    created_at: datetime | None = None


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
