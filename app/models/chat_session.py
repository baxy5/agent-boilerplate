import enum

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.services.database import Base


class TypeEnum(enum.Enum):
  user = "user"
  assistant = "assistant"


class Message(Base):
  __tablename__ = "messages"

  id = Column(Integer, primary_key=True, nullable=False)
  session_id = Column(Integer, ForeignKey("chat_sessions.session_id"), nullable=False)
  type = Column(Enum(TypeEnum), nullable=False)
  content = Column(String, nullable=False)
  option = Column(JSON, nullable=True)

  session = relationship("ChatSession", back_populates="messages")


class ChatSession(Base):
  __tablename__ = "chat_sessions"

  session_id = Column(Integer, primary_key=True, nullable=False)
  title = Column(String(500), nullable=False)
  messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
