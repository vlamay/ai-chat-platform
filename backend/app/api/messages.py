from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from fastapi_cache.decorator import cache
from app.core.database import get_db
from app.models import Chat, Message
from app.schemas.chat import MessageCreateRequest, MessageResponse
from app.api.deps import get_current_user_from_header
from app.services.claude import stream_claude_response

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/{chat_id}", response_model=list[MessageResponse])
@cache(expire=60)  # Cache for 1 minute
async def get_messages(
    chat_id: str,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user_from_header(authorization, db)

    # Verify chat belongs to user
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id).where(Chat.user_id == user.id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    # Get messages
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
    )
    messages = result.scalars().all()

    return messages


@router.post("/{chat_id}/stream")
async def stream_message(
    chat_id: str,
    message_data: MessageCreateRequest,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Stream message response from Claude"""
    from fastapi.responses import StreamingResponse

    user = await get_current_user_from_header(authorization, db)

    # Verify chat belongs to user
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id).where(Chat.user_id == user.id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    # Save user message
    user_message = Message(chat_id=chat_id, role="user", content=message_data.content)
    db.add(user_message)
    await db.commit()

    # Get chat history
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
    )
    messages = result.scalars().all()

    # Format for Claude
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

    # Create streaming response
    async def generate():
        full_response = ""
        async for chunk in stream_claude_response(formatted_messages, chat.model):
            full_response += chunk
            yield f"data: {chunk}\n\n"

        # Save assistant message
        assistant_message = Message(
            chat_id=chat_id, role="assistant", content=full_response
        )
        db.add(assistant_message)
        await db.commit()

        # Update chat timestamp
        chat.updated_at = datetime.utcnow()
        await db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")
