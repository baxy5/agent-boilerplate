from typing import Annotated

from fastapi import Depends
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver, RunnableConfig
from langgraph.graph import END, StateGraph

from app.agents.chat_agent_example import ChatAgentExample
from app.agents.graph_example import get_checkpointer
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

    self.graph = self._build_multi_agent_graph()

  def _build_multi_agent_graph(self):
    """Build the multi-agent workflow graph."""
    graph = StateGraph(MultiAgentState)

    graph.add_node("supervisor_agent", self.supervisor_agent.supervise)
    graph.add_node("research_agent", self.research_agent.research)
    graph.add_node("summary_agent", self.summary_agent.summary)
    graph.add_node("chat_agent", self.chat_agent.chat)

    def route_to_agent(state: MultiAgentState):
      current_agent = state.get("current_agent", "supervisor")

      if current_agent == "END":
        return END
      elif current_agent in ["supervisor", "researcher", "summary", "chat"]:
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
        END: END,
      },
    )

    return graph.compile(checkpointer=self.checkpointer)

  async def generate(self, req: MultiAgentRequest):
    """"""
    config = RunnableConfig(configurable={"thread_id": req.session_id})

    existing_messages = []
    current_state = await self.graph.aget_state(config=config)
    if current_state and current_state.values:
      existing_messages = current_state.values.get("messages", [])

    initial_state = {
      "research_data": "",
      "summary_data": "",
      "iteration_count": 0,
      "agent_decisions": {},
      "messages": existing_messages + [HumanMessage(content=req.input)],
    }

    final_state = await self.graph.ainvoke(initial_state, config)

    return final_state["messages"][-1].content
