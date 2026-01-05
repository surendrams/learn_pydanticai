from pydantic import BaseModel
from pydantic_ai import Agent

import os
from dotenv import find_dotenv, load_dotenv

# 1. Define the "Shape" of the data we want back (The Result Schema)
class CityWeather(BaseModel):
    city: str
    temperature: float
    unit: str
    summary: str

load_dotenv(find_dotenv())
# 2. Initialize the Agent
# We tell it which model to use and what the result type should be.
agent = Agent(
    model='gemini-3-flash-preview',
    output_type=CityWeather,
    instructions="You are a helpful weather assistant."
)

# 3. Run the agent
result = agent.run_sync("What is the weather like in London today?")

# 4. Access the data safely
# 'result.data' is an instance of the CityWeather class.
print(f"City: {result.output.city}")
print(f"Summary: {result.output.summary}")
print(result.all_messages()) 
print(result.usage())