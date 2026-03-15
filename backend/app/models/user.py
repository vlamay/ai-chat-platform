from sqlalchemy import Column, String, DateTime, func, Uuid
import uuid
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True, native_uuid=False), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User {self.email}>"
