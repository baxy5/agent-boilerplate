import operator
from typing import Annotated, Dict, Sequence, TypedDict

from langchain_core.messages import AnyMessage
from pydantic import BaseModel


class MultiAgentState(TypedDict):
  current_agent: str
  research_data: str
  iteration_count: int = 0
  agent_decisions: Dict[str, str]
  messages: Annotated[Sequence[AnyMessage], operator.add]


class MultiAgentRequest(BaseModel):
  input: str
  session_id: str
