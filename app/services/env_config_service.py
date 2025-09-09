import os

from dotenv import load_dotenv

load_dotenv()


class EnvConfigService:
  """Environment variable configuration class."""

  def get_openai_api_key(self) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
      raise RuntimeError("OPENAI_API_KEY is not set.")
    return key
