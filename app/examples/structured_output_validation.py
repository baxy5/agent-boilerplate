import json
import os

from dotenv import load_dotenv
from jsonschema import ValidationError, validate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
  raise EnvironmentError("OPENAI_API_KEY is not set.")


"""
This example demonstrates the difference between validated and non-validated structured output.

The code illustrates how output validation can:
- Ensure data consistency
- Catch formatting errors
- Provide type safety
- Improve reliability in data processing pipelines
- Eliminate hallucinations

Compare both approaches to understand when validation is beneficial for your use case.
"""

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

config = {"configurable": {"thread_id": "abc123"}}

""" Example for validating with Pydantic model. """


class OutputSchema(BaseModel):
  text: str = Field(
    description="Additional description text to explain what happened and what is the output."
  )
  option: dict = Field(description="Echart option schema as a JSON object.")


llm_with_structured_output = llm.with_structured_output(method="json_mode")

output = llm_with_structured_output.invoke(
  "Give me a simple line chart example using Echart. "
  "Please respond in JSON format with both 'text' (description), 'title' (title) and 'option' (ECharts configuration object) fields."
)
print(output)
print("-----------------------------------------------")

validated_output = OutputSchema.model_validate(output)
print(validated_output.model_dump())

""" Example for validating with jsonschema. """

output_schema = {
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "Additional description text to explain what happened and what is the output.",
    },
    "option": {
      "type": "object",
      "properties": {
        "xAxis": {
          "type": "object",
          "properties": {
            "type": {"type": "string", "enum": ["category", "value", "time", "log"]},
            "data": {"type": "array", "items": {"type": "string"}},
          },
          "required": ["type"],
        },
        "yAxis": {
          "type": "object",
          "properties": {"type": {"type": "string", "enum": ["category", "value", "time", "log"]}},
          "required": ["type"],
        },
        "series": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "data": {"type": "array", "items": {"type": "number"}},
              "type": {"type": "string", "enum": ["line", "bar", "pie", "scatter"]},
            },
            "required": ["data", "type"],
          },
        },
      },
      "required": ["xAxis", "yAxis", "series"],
      "description": "ECharts line chart configuration object",
    },
  },
  "required": ["text", "option"],
}

""" 
Comment: this validation is not that trusting, because gave back successfull even
when the 'title' was there.
"""
print("-----------------------------------------------")
print("JSON Schema validation:")

try:
  print(validate(instance=output, schema=output_schema))
  print("✅ JSON Schema validation successful!")
  print("Validated output structure:")
  print(json.dumps(output, indent=2))
except ValidationError as e:
  print(f"❌ JSON Schema validation error: {e.message}")
  print(f"Failed at path: {' -> '.join(str(x) for x in e.absolute_path)}")
except Exception as e:
  print(f"❌ Validation error: {e}")
