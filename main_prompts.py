from pydantic_ai import Agent, RunContext
from dotenv import find_dotenv, load_dotenv
from datetime import date


load_dotenv(find_dotenv())

# 2. Initialize the Agent
# We tell it which model to use and what the result type should be.
agent = Agent(
    model='gemini-3-flash-preview',
    deps_type=str
)

# 1. A Static System Prompt (The Foundation)
@agent.system_prompt
def base_instruction() -> str:
    return "You are a professional research assistant."

# 2. A Dynamic System Prompt (The Context)
@agent.system_prompt
def current_date_instruction() -> str:
    # This is calculated every time agent.run() is called
    return f"Today's date is {date.today()}. Use this for any time-based queries."

@agent.system_prompt
def personalize_prompt(ctx: RunContext[str]) -> str:
    # ctx.deps here is the user's name we pass in later
    return f"The user's name is {ctx.deps}. Address them politely."

# 3. Running the agent
result = agent.run_sync("How many years has it been since the moon landing (1969)?", deps="Alice")
print(result.output)