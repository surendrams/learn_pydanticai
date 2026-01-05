import os
import asyncio

from dotenv import find_dotenv, load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner

# Import your logic from the previous specialist file
from lumi_system_02 import run_lumi_flow

load_dotenv(find_dotenv())

async def generate_quiz(user_request: str) -> str:
    """Triggers the multi-agent flow and returns a summary."""
    print(f"🔄 ADK Orchestrator: Triggering internal workflow for '{user_request}'")
    
    quiz_data = await run_lumi_flow(user_request)
    
    if quiz_data:
        # Create the string once and return it
        summary = (
            f"Successfully generated a quiz. "
            f"Contains {len(quiz_data.questions)} questions. Saved to MongoDB."
        )
        return summary
        
    return "I encountered an error while generating the quiz."

# --- 1. THE ADK AGENT DEFINITION ---

# The ADK Agent is the high-level entry point. 
# It handles the conversation and decides when to trigger tools.
lumi_orchestrator = Agent(
    name="lumi_orchestrator",
    model=os.getenv('GOOGLE_MODEL', default='gemini-3-flash-preview'),  # Changed to a valid Gemini model
    description="The primary entry point for the Lumi STEM Quiz system.",
    instruction=(
        "You are the Lumi ADK Orchestrator. Your goal is to help users create "
        "STEM quizzes. When a user asks for a quiz, call the 'generate_quiz' tool. "
        "If the request is missing a subject or grade level, ask the user to clarify "
        "before proceeding."
    ),
    tools=[generate_quiz]
)

async def main():
    from google.adk.apps import App
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    # 1. Initialize Services
    session_service = InMemorySessionService()
    
    # !!! MANDATORY STEP: Create the session in the service first !!!
    await session_service.create_session(
        app_name="lumi_quiz_app",
        user_id="default_user",
        session_id="lumi_session_001"
    )

    lumi_app = App(
        name="lumi_quiz_app",
        root_agent=lumi_orchestrator
    )
    
    # 2. Setup Runner
    runner = Runner(app=lumi_app, session_service=session_service)
    
    user_input = "I need 3 hard Algebra 1 Advanced questions about polynomials for a 9th grader."
    new_message = types.Content(
        role="user", parts=[types.Part(text=user_input)]
    )
    
    print("🚀 Lumi ADK: Starting session...")
    
    async for event in runner.run_async(
        new_message=new_message,
        user_id="default_user",
        session_id="lumi_session_001"
    ):
        # Handle the event - use getattr to safely access attributes
        text = getattr(event, 'text', None)
        if text:
            print(f"🤖 Lumi: {text}")
        else:
            content = getattr(event, 'content', None)
            if content:
                print(f"🤖 Lumi: {content}")
        

if __name__ == "__main__":
    # Ensure your GOOGLE_API_KEY is in your environment
    asyncio.run(main()) 

