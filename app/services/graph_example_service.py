from typing import Annotated

from fastapi import Depends, HTTPException

from app.examples.graph_example import ExampleGraph


class GraphExampleService:
  def __init__(self, agent: Annotated[ExampleGraph, Depends()]):
    self.agent = agent

  async def generate(self, input: str, thread_id: str):
    try:
      config = {"configurable": {"thread_id": thread_id}}

      initial_state = {"input": input, "output": "", "chat_history": []}

      response = await self.agent.graph.ainvoke(initial_state, config=config)

      return response["output"]

    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Example graph generation have failed, {e}")
