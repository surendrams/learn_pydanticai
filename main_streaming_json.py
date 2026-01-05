from pydantic_ai import Agent
from pydantic import BaseModel

from dotenv import find_dotenv, load_dotenv
import asyncio

load_dotenv(find_dotenv())

class UserProgress(BaseModel):
    percentage: int
    status_message: str

agent = Agent('gemini-3-flash-preview', output_type=UserProgress)

async def main():
    print("=== Approach 1: Stream text chunks (shows real-time progress) ===")
    async with agent.run_stream("Write a 500-word essay on Cobol....") as result:
        async for text in result.stream_text():
            # Raw text chunks as they're generated
            print(text, end='', flush=True)
        print("\n")

    print("\n=== Approach 2: Stream structured output (may only show at end) ===")
    async with agent.run_stream("Write a 500-word essay on Cobol....") as result:
        async for message in result.stream_output():
            # 'message' is a PARTIAL version of UserProgress during streaming
            # Note: This may only yield once at the end for structured outputs
            print(f"Status: {message.status_message} ({message.percentage}%)")

if __name__ == '__main__':
    asyncio.run(main())
