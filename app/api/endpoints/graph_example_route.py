from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.models.example_model import MultiAgentRequest
from app.services.graph_example_service import GraphExampleService
from app.services.multi_agent_orchestrator_example import MultiAgentOrchestratorExample

router = APIRouter()


@router.post("/")
async def example_generate(
  input: str, thread_id: str, service: Annotated[GraphExampleService, Depends()]
):
  try:
    return await service.generate(input, thread_id)
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Example graph generation have failed, {e}")


@router.post("/multi")
async def multi_example_generate(
  req: MultiAgentRequest, service: Annotated[MultiAgentOrchestratorExample, Depends()]
):
  try:
    return await service.generate(req)
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Multi agent example generation have failed, {e}")
