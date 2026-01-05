import asyncio
import os
from enum import Enum
from typing import List

import logfire
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

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

# 1. Initialize the Provider with your API key
# This is where the api_key actually goes now
google_provider = GoogleProvider(
    api_key=os.getenv('GOOGLE_API_KEY')
)

# 2. Initialize the Model using that provider
model = GoogleModel(
    model_name='gemini-3-flash-preview',
    provider=google_provider
)
# 2. Agent Initialization (Same as before, but with direct model)
agent = Agent(
    model=model,
    output_type=QuestionBank,
    instructions="You are a helpful STEM tutor. Return Algebra questions in JSON.",
    retries=3
)

async def main():
    # This will now work without the 400 'thought_signature' error!
    result = await agent.run("Generate 2 questions on Algebra 1.")
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())