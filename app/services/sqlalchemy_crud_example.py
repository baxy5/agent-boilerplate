from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession


class OrmCrudExample:
  def __init__(self, db: Session):
    self.session = db

  def lifecheck(self):
    return {"status": "alive", "database": "connected"}

  def add_chat_session(self, session_id: str):
    title = f"Session id: {session_id}"
    try:
      if session_id and title:
        new_chat_session = ChatSession(session_id=session_id, title=title)
        self.session.add(new_chat_session)
        self.session.commit()
        self.session.refresh(new_chat_session)  # refresh to get autoincrement ID
        return {"session_id": session_id, "title": title}
      else:
        raise HTTPException(status_code=400, detail="session_id and title are required")
    except Exception as e:
      self.session.rollback()
      raise HTTPException(status_code=500, detail=f"New chat session insertion failed: {e}")

  def delete_chat_session(self, session_id: str):
    try:
      stmt = select(ChatSession).where(ChatSession.session_id == session_id)
      chat_session = self.session.scalars(stmt).first()
      if chat_session:
        self.session.delete(chat_session)
        self.session.commit()
    except Exception as e:
      self.session.rollback()
      raise HTTPException(status_code=500, detail=f"Session deletion failed: {e}")
