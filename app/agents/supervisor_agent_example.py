from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from app.models.example_model import MultiAgentState
from app.services.env_config_service import EnvConfigService


class SupervisorAgentExample:
  """Example agent for routing tasks to appropriate agents and manages workflow."""

  def __init__(self, env_config: EnvConfigService):
    self.env_config = env_config
    self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=env_config.OPENAI_API_KEY)

  async def supervise(self, state: MultiAgentState):
    """"""
    messages = state["messages"]
    last_message = messages[-1]

    if not last_message:
      return {"current_agent": "supervisor"}

    # Supervisor prompt
    supervisor_prompt = f"""
    You are a supervisor agent managing a multi-agent system. 
    Analyze the following user request and determine the best workflow:
    
    User request: {last_message.content if hasattr(last_message, "content") else str(last_message)}
    
    Available agents:
    1. researcher - For web searches and information gathering
    2. summary - For creating final responses and content
    3. chat - Handles direct questions, requirements or just chatting that don't require other agents' collaboration
    
    Current state:
    - Research data available: {bool(state.get("research_data"))}
    - Summary completed: {bool(state.get("summary_data"))}
    - Iteration: {state.get("iteration_count", 0)}
    
    Respond with ONLY the next agent name that should handle this task: researcher, summary, chat or END.
    """

    system_message = SystemMessage(content=supervisor_prompt)
    response = await self.llm.ainvoke([system_message])

    next_agent = response.content.strip().lower()

    print(f"Iteration count: {state.get('iteration_count', 0)}")
    if state.get("iteration_count", 0) > 5:
      next_agent = "END"
    elif not state.get("research_data") and next_agent != "chat":
      next_agent = "researcher"
    elif state.get("research_data"):
      next_agent = "summary"

    # decision_message = AIMessage(content=f"Supervisor decision: Route to {next_agent}")
    print(f"Supervisor decision: Route to {next_agent}")

    return {
      #   "messages": [decision_message],
      "current_agent": next_agent,
      "agent_decisions": {**state.get("agent_decisions", {}), "supervisor": next_agent},
      "iteration_count": state.get("iteration_count", 0) + 1,
    }
