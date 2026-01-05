import asyncio
import os
import re
from enum import Enum
from typing import List

import logfire
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

load_dotenv(find_dotenv())

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

# --- 1. CONFIGURATION & MODELS ---
google_provider = GoogleProvider(api_key=os.getenv('GOOGLE_API_KEY'))
model = GoogleModel('gemini-3-flash-preview', provider=google_provider)



# --- 2. THE VALIDATION UTILITY ---
def validate_latex_format(text: str):
    """Checks for balanced $ and converts < > to \lt \gt."""
    total_dollars = len(re.findall(r'(?<!\\)\$', text))
    if total_dollars % 2 != 0:
        raise ModelRetry("Unbalanced LaTeX $ delimiters. Ensure every $ is closed.")
    if '<' in text or '>' in text:
        # Check if inside math (simplistic check for this example)
        if '$' in text:
            raise ModelRetry("Use \\lt or \\gt instead of < or > inside math blocks.")

# --- 3. AGENT DEFINITIONS ---

# The Validator Agent (The Professor)
validator_agent = Agent(
    model=model,
    system_prompt="Check math questions for logical accuracy. If incorrect, reply with 'FIX: [reason]'."
)

# The Tutor Agent (The Creator)
tutor_agent = Agent(
    model=model,
    output_type=QuestionBank,
    instructions="You are a STEM Tutor. Use $ for math. Output exactly 2 questions."
)

# Change from @tutor_agent.result_validator to:
@tutor_agent.output_validator
async def master_validation_loop(ctx: RunContext[None], bank: QuestionBank) -> QuestionBank:
    # 1. Formatting Check (Regex)
    for q in bank.questions:
        validate_latex_format(q.question_text)
        validate_latex_format(q.explanation)
    
    # 2. Logical Check (AI Validator)
    critique = await validator_agent.run(f"Review these: {bank.model_dump_json()}")
    if "FIX:" in critique.output.upper():
        raise ModelRetry(f"Logic Error: {critique.output}")
    
    return bank

# --- 4. THE ORCHESTRATOR (The Extractor) ---
async def run_lumi_system(topic: str):
    print(f"--- Processing Topic: {topic} ---")
    try:
        # The tutor_agent handles the creation and internal validation
        result = await tutor_agent.run(f"Topic: {topic}")
        return result.output
    except Exception as e:
        print(f"System Error: {e}")
        return None

if __name__ == "__main__":
    async def test():
        bank = await run_lumi_system("Algebra 1: Factoring Quadratics")
        if bank:
            print(f"\nFinal Bank for {bank}:")
            for q in bank.questions:
                print(f"- {q}\n")

    asyncio.run(test())
