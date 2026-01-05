import asyncio
import os

from attr import dataclass
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv(find_dotenv())

# 1. Define the Output Schema
@dataclass
class ScienceFact(BaseModel):
    topic: str
    fact: str
    complexity_level: str

# 2. Configure the Provider for OpenRouter
# This is the new way to handle non-default API endpoints
openrouter_provider = OpenAIProvider(
    base_url=os.getenv('OPENROUTER_BASE_URL'),
    api_key=os.getenv('OPENROUTER_API_KEY')
)

# 3. Initialize the Model using the new OpenAIChatModel class
# We pass the provider explicitly here
model = OpenAIChatModel(
    model_name='google/gemini-2.0-flash-001',
    provider=openrouter_provider
)

# 4. Initialize the Agent
agent = Agent(
    model=model,
    output_type=ScienceFact,
    instructions="You are a helpful science tutor. Return interesting facts in structured JSON."
)

async def main():
    result = await agent.run("Tell me something about quantum entanglement.")
    
    print(f"Topic.    : {result.output.topic}")
    print(f"Fact.     : {result.output.fact}")
    print(f"Complexity: {result.output.complexity_level}")

if __name__ == "__main__":
    asyncio.run(main()) 