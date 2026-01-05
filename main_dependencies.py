from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, ModelRetry, RunContext
import asyncio

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient


agent = Agent(
    'gemini-3-flash-preview',
    deps_type=MyDeps,
)


@agent.system_prompt
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:
    # Mock implementation - replace with real API endpoint
    return 'You are a helpful comedian assistant. Tell jokes based on the user request.'


@agent.tool
async def get_joke_material(ctx: RunContext[MyDeps], subject: str) -> str:
    # Mock implementation - replace with real API endpoint
    return f'Here are some joke ideas about {subject}: wordplay, puns, and observations.'


@agent.output_validator
async def validate_output(ctx: RunContext[MyDeps], output: str) -> str:
    # Mock implementation - replace with real validation endpoint
    # Simple validation: ensure output is not empty
    if not output or len(output.strip()) < 5:
        raise ModelRetry('Output is too short, please provide a longer response.')
    return output


async def main():
    print('Main')
    async with httpx.AsyncClient() as client:
        print('Before calling')
        deps = MyDeps('foobar', client)
        result = await agent.run('Tell me a joke.', deps=deps)
        print(result.output)
        print('After calling')
        #> Did you hear about the toothpaste scandal? They called it Colgate.
        
if __name__ == '__main__':
    asyncio.run(main())
    