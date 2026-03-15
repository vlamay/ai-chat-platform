from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class MessageBase(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    tokens_used: int | None = None


class MessageResponse(MessageBase):
    id: UUID
    chat_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatBase(BaseModel):
    title: str = "New Chat"
    model: str = "claude-haiku-4-5-20251001"


class ChatCreate(ChatBase):
    pass


class ChatUpdate(BaseModel):
    title: str | None = None
    model: str | None = None


class ChatResponse(ChatBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ChatListResponse(BaseModel):
    id: UUID
    title: str
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class MessageCreateRequest(BaseModel):
    content: str
