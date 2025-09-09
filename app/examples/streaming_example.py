import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY is not set.") 

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

config = {"configurable": {"thread_id": "abc123"}}

for chunk in llm.stream("Hi, my name is Janos. Who are you?", config=config):
    print(chunk.content, end="", flush=True)
