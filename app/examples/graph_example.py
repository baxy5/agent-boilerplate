import operator
from typing import Annotated, Sequence, TypedDict

from fastapi import Depends, Request
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

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
    self.tools = [self._create_tavily_tool()]
    self.graph = self._build_graph()

  def _create_tavily_tool(self):
    @tool
    async def tavily_search_tool(input: str) -> str:
      """Example web search tool."""
      tool = TavilySearch(api_key=self.env_config.TAVILY_API_KEY, max_results=1)
      result = tool.invoke(input)
      return result["results"][0]["content"]

    return tavily_search_tool

  def _build_graph(self):
    graph = StateGraph(AgentState)

    async def generate_response(state: AgentState):
      client = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=self.env_config.OPENAI_API_KEY,
        streaming=True,
      )

      client_with_tools = client.bind_tools(self.tools)

      messages = state["messages"]

      # Add system message only if it's the first interaction
      if not messages or not any(isinstance(msg, SystemMessage) for msg in messages):
        system_message = SystemMessage(
          "You are a helpful assistant, your task is to answer the user's questions."
        )
        messages = [system_message] + list(messages)

      try:
        response = await client_with_tools.ainvoke(messages)

        return {"messages": [response]}
      except Exception as e:
        raise Exception(f"Error while generating response. {e}")

    def router(state: AgentState):
      messages = state["messages"]
      last_message = messages[-1]

      if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

      return END

    graph.add_node("generate_response", generate_response)
    graph.add_node("tools", ToolNode(self.tools))

    graph.set_entry_point("generate_response")

    graph.add_conditional_edges("generate_response", router, {"tools": "tools", END: END})

    graph.add_edge("tools", "generate_response")

    return graph.compile(checkpointer=self.checkpoint_saver)
