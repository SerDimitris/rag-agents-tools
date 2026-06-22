import uuid
from typing import Any

from fastapi import APIRouter
from sqlmodel import col, func, select

from app.agents.chatbot import generate_chat_reply
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ChatMessage,
    ChatMessageCreate,
    ChatMessagePublic,
    ChatMessageRole,
    ChatMessagesPublic,
    ChatResponse,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages", response_model=ChatMessagesPublic)
def read_chat_messages(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve chat messages for the current user.
    """
    count_statement = (
        select(func.count())
        .select_from(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(col(ChatMessage.created_at).asc())
        .offset(skip)
        .limit(limit)
    )
    messages = session.exec(statement).all()
    return ChatMessagesPublic(
        data=[ChatMessagePublic.model_validate(message) for message in messages],
        count=count,
    )


@router.post("/messages", response_model=ChatResponse)
def send_chat_message(
    *, session: SessionDep, current_user: CurrentUser, message_in: ChatMessageCreate
) -> Any:
    """
    Send a message to the document chatbot and receive a reply.
    """
    reply_content = generate_chat_reply(
        session=session,
        user_id=current_user.id,
        user_message=message_in.content,
    )

    user_message = ChatMessage(
        user_id=current_user.id,
        role=ChatMessageRole.user,
        content=message_in.content,
    )
    assistant_message = ChatMessage(
        user_id=current_user.id,
        role=ChatMessageRole.assistant,
        content=reply_content,
    )
    session.add(user_message)
    session.add(assistant_message)
    session.commit()
    session.refresh(user_message)
    session.refresh(assistant_message)

    return ChatResponse(
        user_message=ChatMessagePublic.model_validate(user_message),
        assistant_message=ChatMessagePublic.model_validate(assistant_message),
    )
