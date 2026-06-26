import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.agents.chatbot import complete_chat_reply, prepare_chat_reply
from app.api.deps import CurrentUser, SessionDep, get_customer_or_404
from app.api.routes.chat_helpers import feedback_by_message_id, to_chat_message_public
from app.models import (
    ChatMessage,
    ChatMessageCreate,
    ChatMessageRole,
    ChatMessagesPublic,
    ChatResponse,
    MessageFeedback,
    MessageFeedbackCreate,
    MessageFeedbackPublic,
)

router = APIRouter(prefix="/chat", tags=["chat"])


def _load_feedback_for_messages(
    session: SessionDep,
    current_user: CurrentUser,
    message_ids: list[uuid.UUID],
) -> dict[uuid.UUID, MessageFeedback]:
    if not message_ids:
        return {}

    statement = (
        select(MessageFeedback)
        .where(MessageFeedback.user_id == current_user.id)
        .where(col(MessageFeedback.message_id).in_(message_ids))
    )
    rows = session.exec(statement).all()
    return feedback_by_message_id(list(rows))


@router.get("/messages", response_model=ChatMessagesPublic)
def read_chat_messages(
    session: SessionDep,
    current_user: CurrentUser,
    customer_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve chat messages for the current user and customer.
    """
    get_customer_or_404(session, customer_id)

    count_statement = (
        select(func.count())
        .select_from(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .where(ChatMessage.customer_id == customer_id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .where(ChatMessage.customer_id == customer_id)
        .order_by(col(ChatMessage.created_at).asc())
        .offset(skip)
        .limit(limit)
    )
    messages = session.exec(statement).all()
    assistant_ids = [
        message.id for message in messages if message.role == ChatMessageRole.assistant
    ]
    feedback_map = _load_feedback_for_messages(session, current_user, assistant_ids)

    return ChatMessagesPublic(
        data=[
            to_chat_message_public(
                message,
                feedback_map.get(message.id),
            )
            for message in messages
        ],
        count=count,
    )


@router.post("/messages", response_model=ChatResponse)
async def send_chat_message(
    *, session: SessionDep, current_user: CurrentUser, message_in: ChatMessageCreate
) -> Any:
    """
    Send a message to the document chatbot and receive a reply.
    """
    get_customer_or_404(session, message_in.customer_id)

    prepared = prepare_chat_reply(
        session=session,
        user_id=current_user.id,
        customer_id=message_in.customer_id,
        user_message=message_in.content,
    )
    reply = await asyncio.to_thread(complete_chat_reply, prepared)

    user_message = ChatMessage(
        user_id=current_user.id,
        customer_id=message_in.customer_id,
        role=ChatMessageRole.user,
        content=message_in.content,
    )
    session.add(user_message)
    session.flush()

    assistant_message = ChatMessage(
        user_id=current_user.id,
        customer_id=message_in.customer_id,
        role=ChatMessageRole.assistant,
        content=reply.content,
        reply_to_id=user_message.id,
        rag_trace=reply.rag_trace,
    )
    session.add(assistant_message)
    session.commit()
    session.refresh(user_message)
    session.refresh(assistant_message)

    return ChatResponse(
        user_message=to_chat_message_public(user_message),
        assistant_message=to_chat_message_public(assistant_message),
    )


@router.post("/messages/{message_id}/feedback", response_model=MessageFeedbackPublic)
def submit_message_feedback(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: uuid.UUID,
    feedback_in: MessageFeedbackCreate,
) -> Any:
    """
    Submit or update feedback on an assistant chat message.
    """
    message = session.get(ChatMessage, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.role != ChatMessageRole.assistant:
        raise HTTPException(
            status_code=400, detail="Feedback is only allowed on assistant messages"
        )

    get_customer_or_404(session, message.customer_id)

    statement = (
        select(MessageFeedback)
        .where(MessageFeedback.message_id == message_id)
        .where(MessageFeedback.user_id == current_user.id)
    )
    existing = session.exec(statement).first()

    if existing is None:
        feedback = MessageFeedback(
            message_id=message_id,
            user_id=current_user.id,
            rating=feedback_in.rating,
            reason=feedback_in.reason,
            comment=feedback_in.comment,
        )
        session.add(feedback)
    else:
        existing.rating = feedback_in.rating
        existing.reason = feedback_in.reason
        existing.comment = feedback_in.comment
        feedback = existing

    session.commit()
    session.refresh(feedback)
    return MessageFeedbackPublic.model_validate(feedback)
