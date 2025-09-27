from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.database import get_db
from app.services.sqlalchemy_crud_example import OrmCrudExample

router = APIRouter()


def get_db_session(db: Session = Depends(get_db)) -> OrmCrudExample:
  return OrmCrudExample(db)


@router.get("/lifecheck")
async def lifecheck(service: Annotated[OrmCrudExample, Depends(get_db_session)]):
  try:
    return service.lifecheck()
  except Exception:
    raise HTTPException(status_code=500, detail="Lifecheck failed.")


@router.post("/add_session")
async def add_session(session_id: str, service: Annotated[OrmCrudExample, Depends(get_db_session)]):
  try:
    result = service.add_chat_session(session_id=session_id)
    return result
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Add session failed: {e}")


@router.delete("/delete_session")
async def delete_session(
  session_id: str, service: Annotated[OrmCrudExample, Depends(get_db_session)]
):
  try:
    result = service.delete_chat_session(session_id)
    return result
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Delete session failed: {e}")
