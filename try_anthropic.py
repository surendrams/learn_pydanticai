from pydantic_ai import Agent
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Using the shorthand notation
agent = Agent('anthropic:claude-sonnet-4-5')

# Or with explicit model initialization
from pydantic_ai.models.anthropic import AnthropicModel
model = AnthropicModel('claude-sonnet-4-5')
agent = Agent(model)
result = agent.run_sync("Write 500 word essay about cobol")
print(f"{result.output}")