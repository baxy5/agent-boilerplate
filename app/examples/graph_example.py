import os
import asyncio
import sys
from typing import TypedDict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY is not set.")
    
class AgentState(TypedDict):
    input: str
    output: Any

class ExampleGraph:
    """ This Graph implementation serves only for example purposes. """
    def __init__(self):
        self.graph = self._build_graph()
        
    def _build_graph(self):
        graph = StateGraph(AgentState)
        
        async def generate_response(state: AgentState):
            client = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, streaming=True)
            
            try:
                messages = [
                    SystemMessage("You are a helpful assistant, your task is to answer the user's questions."),
                    HumanMessage(state["input"])
                ]
                
                response = client.astream(messages)
                state["output"] = response
                return state
            except Exception as e:
                raise Exception(f"Error while generating response. {e}")
            
        graph.add_node("generate_response", generate_response)
        
        graph.set_entry_point("generate_response")
        graph.add_edge("generate_response", END)
        
        return graph.compile()

    async def run(self, user_input: str):
        initial_state = AgentState(input=user_input, output=None)
        result = await self.graph.ainvoke(initial_state)
        
        full_response = ""
        print("Agent: ", end="", flush=True)
        
        async for chunk in result["output"]:
            if chunk.content:
                print(chunk.content, end="", flush=True)
                full_response += chunk.content
        
        print()
        return full_response



""" Example for running the agent in CMD """
async def main():
    agent = ExampleGraph()
    
    print("Streaming Agent initialized successfully!")
    print("You can now interact with the agent. Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not user_input:
            print("Please enter a question or type 'quit' to exit.")
            continue
            
        try:
            await agent.run(user_input)
            print()
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())