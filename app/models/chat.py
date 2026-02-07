from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
import uuid
import enum
from sqlalchemy.orm import relationship
from ..core.database import Base


class ChatSender(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PostgresUUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    sender = Column(Enum(ChatSender), nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String(100))
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")