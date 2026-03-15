from sqlalchemy import Column, String, DateTime, ForeignKey, func, Uuid
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Uuid(as_uuid=True, native_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True, native_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False, default="New Chat")
    model = Column(String, nullable=False, default="claude-haiku-4-5-20251001")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chat {self.id}>"
