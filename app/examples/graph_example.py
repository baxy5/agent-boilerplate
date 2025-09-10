import operator
from typing import Annotated, Sequence, TypedDict

from fastapi import Depends, Request
from langchain_core.messages import AIMessage, AnyMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from app.services.env_config_service import EnvConfigService, get_env_configs


def get_checkpointer(req: Request) -> BaseCheckpointSaver:
  return req.app.state.checkpointer


class AgentState(TypedDict):
  messages: Annotated[Sequence[AnyMessage], operator.add]


class ExampleGraph:
  """This Graph implementation serves only for example purposes."""

  def __init__(
    self,
    env_config: Annotated[EnvConfigService, Depends(get_env_configs)],
    checkpointer: Annotated[BaseCheckpointSaver, Depends(get_checkpointer)],
  ):
    self.env_config = env_config
    self.checkpoint_saver = checkpointer
    self.graph = self._build_graph()

  def _build_graph(self):
    graph = StateGraph(AgentState)

    async def generate_response(state: AgentState):
      client = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=self.env_config.OPENAI_API_KEY,
        streaming=True,
      )

      messages = state["messages"]

      # Add system message only if it's the first interaction
      if not messages or not any(isinstance(msg, SystemMessage) for msg in messages):
        system_message = SystemMessage(
          "You are a helpful assistant, your task is to answer the user's questions."
        )
        messages = [system_message] + list(messages)

      try:
        response = await client.ainvoke(messages)

        return {"messages": [AIMessage(content=response.content)]}
      except Exception as e:
        raise Exception(f"Error while generating response. {e}")

    graph.add_node("generate_response", generate_response)

    graph.set_entry_point("generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile(checkpointer=self.checkpoint_saver)
