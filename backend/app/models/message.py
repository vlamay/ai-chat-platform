from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func, Uuid
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid(as_uuid=True, native_uuid=False), primary_key=True, default=uuid.uuid4)
    chat_id = Column(Uuid(as_uuid=True, native_uuid=False), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chat = relationship("Chat", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id}>"
