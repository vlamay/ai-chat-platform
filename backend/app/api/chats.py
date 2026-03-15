from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete
from app.core.database import get_db
from app.models import Chat, Message, User
from app.schemas.chat import ChatCreate, ChatResponse, ChatListResponse, ChatUpdate
from app.services.auth import decode_token, get_user_by_id

router = APIRouter(prefix="/chats", tags=["chats"])


async def get_current_user_from_header(
    authorization: str = Header(None), db: AsyncSession = Depends(get_db)
) -> User:
    """Extract user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await get_user_by_id(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user_from_header(authorization, db)

    chat = Chat(user_id=user.id, title=chat_data.title, model=chat_data.model)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)

    # Return chat without messages to avoid lazy-loading issues
    response = ChatResponse(
        id=chat.id,
        user_id=chat.user_id,
        title=chat.title,
        model=chat.model,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[]
    )
    return response


@router.get("", response_model=list[ChatListResponse])
async def list_chats(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user_from_header(authorization, db)

    # Get chats with message count
    result = await db.execute(
        select(Chat, func.count(Message.id).label("message_count"))
        .where(Chat.user_id == user.id)
        .outerjoin(Message)
        .group_by(Chat.id)
        .order_by(Chat.updated_at.desc())
    )

    chats = []
    for chat, count in result.all():
        chat_dict = ChatListResponse(
            id=chat.id,
            title=chat.title,
            model=chat.model,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            message_count=count or 0,
        )
        chats.append(chat_dict)

    return chats


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user_from_header(authorization, db)

    result = await db.execute(
        select(Chat).where(Chat.id == chat_id).where(Chat.user_id == user.id)
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    # Return chat without messages to avoid lazy-loading issues
    response = ChatResponse(
        id=chat.id,
        user_id=chat.user_id,
        title=chat.title,
        model=chat.model,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[]
    )
    return response


@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: str,
    chat_data: ChatUpdate,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user_from_header(authorization, db)

    result = await db.execute(
        select(Chat).where(Chat.id == chat_id).where(Chat.user_id == user.id)
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    if chat_data.title:
        chat.title = chat_data.title
    if chat_data.model:
        chat.model = chat_data.model

    await db.commit()
    await db.refresh(chat)

    # Return chat without messages to avoid lazy-loading issues
    response = ChatResponse(
        id=chat.id,
        user_id=chat.user_id,
        title=chat.title,
        model=chat.model,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[]
    )
    return response


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user_from_header(authorization, db)

    result = await db.execute(
        select(Chat).where(Chat.id == chat_id).where(Chat.user_id == user.id)
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    await db.execute(delete(Chat).where(Chat.id == chat_id))
    await db.commit()
