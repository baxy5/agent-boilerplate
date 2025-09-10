from typing import Annotated

from fastapi import Depends, HTTPException
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.base import RunnableConfig

from app.examples.graph_example import ExampleGraph


class GraphExampleService:
  def __init__(self, agent: Annotated[ExampleGraph, Depends()]):
    self.agent = agent

  async def generate(self, input: str, thread_id: str):
    try:
      config = RunnableConfig(configurable={"thread_id": thread_id})

      response = await self.agent.graph.ainvoke(
        {"messages": [HumanMessage(content=input)]}, config=config
      )

      return response["messages"][-1].content

    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Example graph generation have failed, {e}")
