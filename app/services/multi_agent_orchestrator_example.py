import json
import os
from typing import Annotated

from fastapi import Depends
from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver, RunnableConfig
from langgraph.graph import END, StateGraph

from app.agents.chat_agent_example import ChatAgentExample
from app.agents.graph_example import get_checkpointer
from app.agents.line_chart_agent_example import LineChartAgentExample
from app.agents.research_agent_example import ResearchAgentExample
from app.agents.summary_agent_example import SummaryAgentExample
from app.agents.supervisor_agent_example import SupervisorAgentExample
from app.models.example_model import MultiAgentRequest, MultiAgentState
from app.services.env_config_service import EnvConfigService, get_env_configs


class MultiAgentOrchestratorExample:
  """Main orchestrator that manages the multi-agent workflow using Langgraph."""

  def __init__(
    self,
    env_config: Annotated[EnvConfigService, Depends(get_env_configs)],
    checkpointer: Annotated[BaseCheckpointSaver, Depends(get_checkpointer)],
  ):
    self.env_config = env_config
    self.checkpointer = checkpointer

    self.supervisor_agent = SupervisorAgentExample(env_config=env_config)
    self.research_agent = ResearchAgentExample(env_config=env_config)
    self.summary_agent = SummaryAgentExample(env_config=env_config)
    self.chat_agent = ChatAgentExample(env_config=env_config)
    self.line_chart_agent = LineChartAgentExample(env_config=env_config)

    self.graph = self._build_multi_agent_graph()

  def _build_multi_agent_graph(self):
    """Build the multi-agent workflow graph."""
    graph = StateGraph(MultiAgentState)

    graph.add_node("supervisor_agent", self.supervisor_agent.supervise)
    graph.add_node("research_agent", self.research_agent.research)
    graph.add_node("summary_agent", self.summary_agent.summary)
    graph.add_node("chat_agent", self.chat_agent.chat)
    graph.add_node("line_chart_agent", self.line_chart_agent.chart)

    def route_to_agent(state: MultiAgentState):
      current_agent = state.get("current_agent", "supervisor")

      if current_agent == "END":
        return END
      elif current_agent in ["supervisor", "researcher", "summary", "chat", "line_chart"]:
        return current_agent
      else:
        return "supervisor"

    graph.set_entry_point("supervisor_agent")

    graph.add_conditional_edges(
      "supervisor_agent",
      route_to_agent,
      {
        "supervisor": "supervisor_agent",
        "researcher": "research_agent",
        "summary": "summary_agent",
        "chat": "chat_agent",
        "line_chart": "line_chart_agent",
        END: END,
      },
    )

    graph.add_conditional_edges(
      "research_agent",
      route_to_agent,
      {
        "supervisor": "supervisor_agent",
        "researcher": "research_agent",
        "summary": "summary_agent",
        "chat": "chat_agent",
        "line_chart": "line_chart_agent",
        END: END,
      },
    )

    graph.add_conditional_edges(
      "summary_agent",
      route_to_agent,
      {
        "supervisor": "supervisor_agent",
        "researcher": "research_agent",
        "summary": "summary_agent",
        "chat": "chat_agent",
        "line_chart": "line_chart_agent",
        END: END,
      },
    )

    graph.add_conditional_edges(
      "chat_agent",
      route_to_agent,
      {
        "supervisor": "supervisor_agent",
        "researcher": "research_agent",
        "summary": "summary_agent",
        "chat": "chat_agent",
        "line_chart": "line_chart_agent",
        END: END,
      },
    )

    graph.add_conditional_edges(
      "line_chart_agent",
      route_to_agent,
      {
        "supervisor": "supervisor_agent",
        "researcher": "research_agent",
        "summary": "summary_agent",
        "chat": "chat_agent",
        "line_chart": "line_chart_agent",
        END: END,
      },
    )

    # pruning_strategy=PruningStrategy.recent(n=3)
    return graph.compile(checkpointer=self.checkpointer)

  def serialise_ai_message_chunk(self, chunk):
    if isinstance(chunk, AIMessageChunk):
      return chunk.content
    else:
      raise TypeError(
        f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
      )

  def draw_graph(self) -> None:
    os.makedirs("images", exist_ok=True)
    self.graph.get_graph().draw_mermaid_png(output_file_path="images/graph.png")

  async def generate(self, req: MultiAgentRequest):
    self.draw_graph()

    config = RunnableConfig(configurable={"thread_id": req.session_id})

    existing_messages = []
    current_state = await self.graph.aget_state(config=config)
    if current_state and current_state.values:
      existing_messages = current_state.values.get("messages", [])

    initial_state = {
      "research_data": "",
      "iteration_count": 0,
      "agent_decisions": {},
      "messages": existing_messages + [HumanMessage(content=req.input)],
    }

    events = self.graph.astream_events(initial_state, version="v2", config=config)

    async for event in events:
      event_type = event["event"]
      event_name = event["name"]
      event_metadata_node = event.get("metadata", {}).get("langgraph_node")

      # Handle progress events when agents start
      if event_type == "on_chain_start":
        if event_name == "research_agent":
          yield 'data: {"type": "progress", "content": "Researching information", "icon": "text_search"}\n\n'
        elif event_name == "summary_agent":
          yield 'data: {"type": "progress", "content": "Summarizing findings", "icon": "notebook"}\n\n'
        elif event_name == "chat_agent":
          yield 'data: {"type": "progress", "content": "Generating response", "icon": "notebook"}\n\n'
        elif event_name == "supervisor_agent":
          yield 'data: {"type": "progress", "content": "Planning next step", "icon": "brain"}\n\n'
        elif event_name == "line_chart_agent":
          yield 'data: {"type": "progress", "content": "Generating line chart", "icon": "notebook"}\n\n'

      # Handle agent completion events
      if event_type == "on_chain_end":
        if event_name == "research_agent":
          yield 'data: {"type": "progress", "content": "Research completed", "icon": "check"}\n\n'
        elif event_name == "summary_agent":
          yield 'data: {"type": "progress", "content": "Summary completed", "icon": "check"}\n\n'
        elif event_name == "chat_agent":
          yield 'data: {"type": "progress", "content": "Response completed", "icon": "check"}\n\n'
        elif event_name == "line_chart_agent":
          event_data = event.get("data", {})
          output = event_data.get("output", {})
          if output and "messages" in output and output["messages"]:
            chart_data = output["messages"][0]
            payload = {"type": "content", "option": chart_data}
            yield f"data: {json.dumps(payload)}\n\n"
          yield 'data: {"type": "progress", "content": "Line chart generation completed", "icon": "check"}\n\n'

      if event_type == "on_tool_start":
        tool_name = event["name"]

        if tool_name == "tavily_search_tool":
          tool_input = event.get("data", {}).get("input", {})
          search_query = tool_input.get("input", "") if isinstance(tool_input, dict) else ""
          payload = {
            "type": "progress",
            "content": "Searching on the web",
            "search_query": search_query,
            "icon": "search",
          }
          yield f"data: {json.dumps(payload)}\n\n"

      if event_type == "on_tool_end":
        tool_name = event["name"]
        if tool_name == "tavily_search_tool":
          payload = {
            "type": "progress",
            "content": "Web search completed",
            "icon": "check",
          }
          yield f"data: {json.dumps(payload)}\n\n"

      # Handle streaming content
      if event_type == "on_chat_model_stream":
        if event_metadata_node == "supervisor_agent":
          continue
        elif event_metadata_node == "research_agent":
          continue
        elif event_metadata_node == "line_chart_agent":
          continue
        else:
          chunk_content = self.serialise_ai_message_chunk(event["data"]["chunk"])
          payload = {"type": "content", "content": chunk_content}
          yield f"data: {json.dumps(payload)}\n\n"

    yield 'data: {"type": "end"}\n\n'
