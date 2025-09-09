import asyncio
from typing import TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph

from app.services.env_config_service import EnvConfigService


class AgentState(TypedDict):
  input: str
  output: str
  chat_history: list[BaseMessage]


class ExampleGraph:
  """This Graph implementation serves only for example purposes."""

  def __init__(self):
    self.envConfig = EnvConfigService()
    self.checkpoint_saver = InMemorySaver()
    self.graph = self._build_graph()

  def _build_graph(self):
    graph = StateGraph(AgentState)

    async def generate_response(state: AgentState):
      client = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=self.envConfig.get_openai_api_key(),
        streaming=True,
      )

      messages = [
        SystemMessage("You are a helpful assistant, your task is to answer the user's questions."),
        *state.get("chat_history", []),
        HumanMessage(state["input"]),
      ]

      try:
        response = await client.ainvoke(messages)

        # Append new messages to history
        updated_history = [
          *state.get("chat_history", []),
          HumanMessage(content=state["input"]),
          AIMessage(content=response.content),
        ]

        state["output"] = response.content
        state["chat_history"] = updated_history
        return state
      except Exception as e:
        raise Exception(f"Error while generating response. {e}")

    graph.add_node("generate_response", generate_response)

    graph.set_entry_point("generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile(checkpointer=self.checkpoint_saver)

  async def run(self, user_input: str, thread_id: str = "asd123"):
    initial_state = AgentState(input=user_input, output="")
    config = {"configurable": {"thread_id": thread_id}}
    result = await self.graph.ainvoke(initial_state, config=config)

    return result["output"]


async def main():
  """Example for running the agent in CMD"""
  agent = ExampleGraph()

  print("You can now interact with the agent. Type 'quit' to exit.\n")

  while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["quit", "exit", "q"]:
      break

    if not user_input:
      print("Please enter a question or type 'quit' to exit.")
      continue

    try:
      response = await agent.run(user_input)
      print("Agent: ", end="", flush=True)
      print(response)
      print()
    except Exception as e:
      print(f"Error: {e}\n")


if __name__ == "__main__":
  asyncio.run(main())
