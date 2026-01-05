import asyncio
import os
from enum import Enum
from typing import List

import httpx
import logfire
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

logfire.configure()
logfire.instrument_pydantic_ai()


class QuestionDifficulty(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_SELECT = "single_select"
    TRUE_FALSE = "true_false"

class QuestionOption(BaseModel):
    """Individual option for a question"""
    id: str = Field(
        ...,
        description="Option identifier (A, B, C, D for MCQ; True, False for true/false)"
    )
    text: str = Field(
        ...,
        min_length=1,
        description="The text content of this option"
    )


class Hint(BaseModel):
    level: int  # 1-3
    text: str

class QuestionDocument(BaseModel):
    question_type: QuestionType
    question_text: str = Field(description="The STEM question. Wrap math in $. Use \\\\ for LaTeX commands.")
    options: List[QuestionOption]
    correct_option: str = Field(description="The ID of the correct answer(s), e.g., 'A' or 'A,C'")
    explanation: str = Field(description="MAX 3 LINES. Explain the logic clearly.")
    hint: str = Field(description="MAX 3 LINES. Give a helpful nudge.")
    
class QuestionBank(BaseModel):
    questions: List[QuestionDocument] = Field(
        default_factory=list,
        description="List of question documents"
    )


load_dotenv(find_dotenv())

# Create an httpx client
http_client = httpx.AsyncClient(
    trust_env=True,  # Use environment proxy settings if available
    timeout=60.0
)

# 2. Configure the Provider for OpenRouter
# This is the new way to handle non-default API endpoints
openrouter_provider = OpenAIProvider(
    base_url=os.getenv('OPENROUTER_BASE_URL'),
    api_key=os.getenv('OPENROUTER_API_KEY'),
    http_client=http_client
)

# 3. Initialize the Model using the new OpenAIChatModel class
# We pass the provider explicitly here
# Using Claude for better structured output support
_model_name = os.getenv('OPENROUTER_MODEL','anthropic/claude-3-5-sonnet-20241022')

model = OpenAIChatModel(
    model_name=_model_name,
    provider=openrouter_provider
)

# 4. Initialize the Agent
agent = Agent(
    model=model,
    output_type=QuestionBank,
    instructions="""You are a helpful STEM tutor. Generate questions as requested by the student.

For math notation: wrap math in $ symbols (e.g., $2x + 5 = 13$) and use \\\\ for LaTeX commands.

Each question should include:
- Multiple choice options (A, B, C, D)
- The correct answer
- A brief explanation (max 3 lines)
- A helpful hint (max 3 lines)"""
,
    retries=3
)

async def main():
    try:
        # Request fewer questions to improve stability during test
        result = await agent.run("Generate 2 Advanced Questions on Algebra 1 for Grade 9 student")
        # Try accessing output, falling back if needed
        
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 