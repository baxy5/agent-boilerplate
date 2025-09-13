"""
Streaming Research Assistant with Visible Reasoning
Demonstrates LangChain + LangGraph streaming with real-time thinking process
"""

import asyncio
import operator
import os
from datetime import datetime
from typing import Annotated, Dict, List, TypedDict

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

# Install required packages:
# pip install langchain langchain-openai langgraph
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
  raise EnvironmentError("OPENAI_API_KEY is not set.")

# =============================================================================
# 1. STATE DEFINITION
# =============================================================================


class ResearchState(TypedDict):
  """State that flows through our research graph"""

  query: str
  thinking_log: Annotated[List[str], operator.add]  # Accumulates thinking steps
  research_steps: Annotated[List[Dict], operator.add]  # Research progress
  final_answer: str
  confidence: float
  sources: List[str]


# =============================================================================
# 2. STREAMING RESEARCH NODES
# =============================================================================


class StreamingResearcher:
  def __init__(self, api_key: str = None):
    """Initialize with OpenAI API key"""
    self.llm = ChatOpenAI(model="gpt-4", temperature=0.3, streaming=True, api_key=OPENAI_API_KEY)

  async def analyze_query(self, state: ResearchState) -> ResearchState:
    """First step: Analyze and plan the research approach"""
    print("🧠 THINKING: Analyzing query...")

    thinking_prompt = ChatPromptTemplate.from_messages(
      [
        (
          "system",
          """You are a research analyst. Analyze the query and create a research plan.
            Think step by step about:
            1. What type of information is needed
            2. What sources would be most reliable
            3. What challenges might arise
            4. How to structure the final answer
            
            Stream your thinking process clearly.""",
        ),
        ("human", "Query: {query}"),
      ]
    )

    # Stream the thinking process
    thinking_steps = []
    async for chunk in self.llm.astream(thinking_prompt.format_messages(query=state["query"])):
      if chunk.content:
        print(f"{chunk.content}", end="", flush=True)
        thinking_steps.append(chunk.content)

    print("\n" + "=" * 50)

    full_thinking = "".join(thinking_steps)

    return {
      **state,
      "thinking_log": [f"ANALYSIS: {full_thinking}"],
      "research_steps": [
        {
          "step": "query_analysis",
          "timestamp": datetime.now().isoformat(),
          "content": full_thinking,
        }
      ],
    }

  async def conduct_research(self, state: ResearchState) -> ResearchState:
    """Second step: Simulate research process with streaming"""
    print("\n📚 THINKING: Conducting research...")

    research_prompt = ChatPromptTemplate.from_messages(
      [
        (
          "system",
          """You are conducting research on the given topic.
            Simulate finding and analyzing information from various sources.
            Think through:
            1. Key facts and findings
            2. Different perspectives
            3. Reliability of information
            4. Gaps in knowledge
            
            Be specific about your research process.""",
        ),
        ("human", "Research topic: {query}\nPrevious analysis: {previous_thinking}"),
      ]
    )

    previous_thinking = state["thinking_log"][-1] if state["thinking_log"] else ""

    research_content = []
    async for chunk in self.llm.astream(
      research_prompt.format_messages(query=state["query"], previous_thinking=previous_thinking)
    ):
      if chunk.content:
        print(f"{chunk.content}", end="", flush=True)
        research_content.append(chunk.content)

    print("\n" + "=" * 50)

    full_research = "".join(research_content)

    # Simulate finding sources
    mock_sources = [
      f"Academic paper on {state['query']}",
      f"Expert analysis of {state['query']}",
      f"Recent study about {state['query']}",
    ]

    return {
      **state,
      "thinking_log": [f"RESEARCH: {full_research}"],
      "research_steps": [
        {
          "step": "research_conduct",
          "timestamp": datetime.now().isoformat(),
          "content": full_research,
        }
      ],
      "sources": mock_sources,
    }

  async def synthesize_answer(self, state: ResearchState) -> ResearchState:
    """Final step: Create the final answer with reasoning"""
    print("\n✍️  THINKING: Synthesizing final answer...")

    synthesis_prompt = ChatPromptTemplate.from_messages(
      [
        (
          "system",
          """Based on your analysis and research, provide a comprehensive answer.
            Think through:
            1. How to structure the response
            2. Key points to emphasize
            3. Confidence level in your answer
            4. Any caveats or limitations
            
            Provide clear, well-reasoned conclusions.""",
        ),
        (
          "human",
          """
            Original query: {query}
            Analysis: {analysis}
            Research: {research}
            
            Synthesize a final answer.
            """,
        ),
      ]
    )

    analysis = state["thinking_log"][0] if len(state["thinking_log"]) > 0 else ""
    research = state["thinking_log"][1] if len(state["thinking_log"]) > 1 else ""

    synthesis_content = []
    async for chunk in self.llm.astream(
      synthesis_prompt.format_messages(query=state["query"], analysis=analysis, research=research)
    ):
      if chunk.content:
        print(f"{chunk.content}", end="", flush=True)
        synthesis_content.append(chunk.content)

    print("\n" + "=" * 50)

    final_answer = "".join(synthesis_content)

    return {
      **state,
      "thinking_log": [f"SYNTHESIS: {final_answer}"],
      "research_steps": [
        {
          "step": "answer_synthesis",
          "timestamp": datetime.now().isoformat(),
          "content": final_answer,
        }
      ],
      "final_answer": final_answer,
      "confidence": 0.85,  # Mock confidence score
    }


# =============================================================================
# 3. GRAPH CONSTRUCTION
# =============================================================================


def create_research_graph(api_key: str = None) -> StateGraph:
  """Create the research workflow graph"""
  researcher = StreamingResearcher(api_key)

  # Create the graph
  workflow = StateGraph(ResearchState)

  # Add nodes
  workflow.add_node("analyze", researcher.analyze_query)
  workflow.add_node("research", researcher.conduct_research)
  workflow.add_node("synthesize", researcher.synthesize_answer)

  # Define the flow
  workflow.set_entry_point("analyze")
  workflow.add_edge("analyze", "research")
  workflow.add_edge("research", "synthesize")
  workflow.add_edge("synthesize", END)

  return workflow.compile()


# =============================================================================
# 4. STREAMING EXECUTION
# =============================================================================


async def run_streaming_research(query: str, api_key: str = None):
  """Run the research process with streaming output"""
  print(f"🚀 Starting research on: '{query}'")
  print("=" * 70)

  # Create the graph
  graph = create_research_graph(api_key)

  # Initial state
  initial_state = {
    "query": query,
    "thinking_log": [],
    "research_steps": [],
    "final_answer": "",
    "confidence": 0.0,
    "sources": [],
  }

  # Stream through the graph
  print("📊 STREAMING RESEARCH PROCESS:")
  print("-" * 40)

  final_state = None
  async for state_update in graph.astream(initial_state):
    # This will stream each node's execution
    for node_name, node_state in state_update.items():
      print(f"\n✅ Completed: {node_name}")
      final_state = node_state

  # Display final results
  print("\n" + "🎯 FINAL RESULTS:")
  print("=" * 70)
  print(f"Query: {final_state['query']}")
  print(f"Confidence: {final_state['confidence']:.2%}")
  print(f"Sources found: {len(final_state['sources'])}")
  print(f"\nFinal Answer:\n{final_state['final_answer']}")

  return final_state


# =============================================================================
# 5. SIMPLE VERSION FOR TESTING WITHOUT API KEY
# =============================================================================


async def demo_without_api():
  """Demo version that works without OpenAI API key"""
  print("🎭 DEMO MODE: Simulating streaming research...")
  print("=" * 70)

  query = "What are the benefits of renewable energy?"

  # Simulate streaming thinking process
  thinking_steps = [
    "Let me analyze this query about renewable energy benefits...",
    "I need to consider economic, environmental, and social aspects...",
    "Key areas to research: cost savings, carbon reduction, job creation...",
    "I should also look at challenges and limitations for balance...",
  ]

  research_steps = [
    "Searching for recent studies on renewable energy economics...",
    "Found data showing 70% cost reduction in solar over past decade...",
    "Wind energy now competitive with fossil fuels in many regions...",
    "Job creation in renewable sector outpacing fossil fuel job losses...",
  ]

  synthesis_steps = [
    "Synthesizing findings into coherent answer...",
    "Main benefits: cost reduction, environmental protection, job creation...",
    "Key challenges: intermittency, storage, initial investment costs...",
    "Overall assessment: strong positive trend with improving technology...",
  ]

  # Simulate streaming
  for i, (phase, steps) in enumerate(
    [("ANALYSIS", thinking_steps), ("RESEARCH", research_steps), ("SYNTHESIS", synthesis_steps)]
  ):
    print(f"\n🧠 {phase} PHASE:")
    print("-" * 40)

    for step in steps:
      # Simulate streaming character by character
      for char in step:
        print(char, end="", flush=True)
        await asyncio.sleep(0.02)  # Simulate typing speed
      print()  # New line after each step
      await asyncio.sleep(0.5)  # Pause between steps

  print("\n🎯 FINAL RESULTS:")
  print("=" * 70)
  print(f"Query: {query}")
  print("Confidence: 88%")
  print("Sources found: 3")
  print("\nFinal Answer:")
  print("Renewable energy offers significant benefits including dramatic cost reductions,")
  print("substantial environmental improvements, and strong job creation potential.")
  print("While challenges like intermittency remain, technological advances continue")
  print("to address these limitations, making renewables increasingly attractive.")


# =============================================================================
# 6. MAIN EXECUTION
# =============================================================================


async def main():
  """Main function - choose your execution mode"""
  print("Choose execution mode:")
  print("1. With OpenAI API (requires API key)")
  print("2. Demo mode (no API key needed)")

  choice = input("Enter choice (1 or 2): ").strip()

  if choice == "1":
    api_key = input("Enter your OpenAI API key: ").strip()
    query = (
      input("Enter your research query: ").strip() or "What are the latest developments in AI?"
    )
    await run_streaming_research(query, api_key)
  else:
    await demo_without_api()


if __name__ == "__main__":
  # Run the example
  asyncio.run(main())
