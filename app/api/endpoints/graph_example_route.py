from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.services.graph_example_service import GraphExampleService

router = APIRouter()


@router.post("/")
async def example_generate(
  input: str, thread_id: str, service: Annotated[GraphExampleService, Depends()]
):
  try:
    return await service.generate(input, thread_id)
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Example graph generation have failed, {e}")
