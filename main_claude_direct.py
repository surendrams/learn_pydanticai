import asyncio
from enum import Enum
from typing import List

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_SELECT = "single_select"
    TRUE_FALSE = "true_false"


class QuestionOption(BaseModel):
    """Individual option for a question"""
    id: str = Field(..., description="Option identifier (A, B, C, D)")
    text: str = Field(..., min_length=1, description="The text content of this option")


class QuestionDocument(BaseModel):
    question_type: QuestionType
    question_text: str = Field(description="The STEM question. Wrap math in $.")
    options: List[QuestionOption]
    correct_option: str = Field(description="The ID of the correct answer, e.g., 'A'")
    explanation: str = Field(description="Brief explanation (max 3 lines)")
    hint: str = Field(description="Helpful hint (max 3 lines)")


class QuestionBank(BaseModel):
    questions: List[QuestionDocument] = Field(
        default_factory=list,
        description="List of question documents"
    )


load_dotenv(find_dotenv())

# Use Claude directly (requires ANTHROPIC_API_KEY in .env)
# Add to .env: ANTHROPIC_API_KEY=your-anthropic-key-here
# The AnthropicModel will automatically read ANTHROPIC_API_KEY from the environment
model = AnthropicModel(
    model_name='claude-3-5-sonnet-20241022'  # Claude has excellent structured output support
)

# Initialize the Agent
agent = Agent(
    model=model,
    output_type=QuestionBank,
    system_prompt="""You are a STEM tutor that generates practice questions.

Generate questions with:
- Clear question text (use $ for math)
- Four options labeled A, B, C, D
- The correct answer ID
- Brief explanation (2-3 lines max)
- Helpful hint (2-3 lines max)""",
    retries=5
)


async def main():
    try:
        result = await agent.run("Generate 2 Advanced Algebra questions for Grade 9")

        print(f"\n{'='*60}")
        print(f"Generated {len(result.output.questions)} questions:")
        print(f"{'='*60}\n")

        for i, q in enumerate(result.output.questions, 1):
            print(f"Question {i}: {q.question_text}")
            print(f"Type: {q.question_type.value}")
            print("\nOptions:")
            for opt in q.options:
                print(f"  {opt.id}) {opt.text}")
            print(f"\nCorrect Answer: {q.correct_option}")
            print(f"Explanation: {q.explanation}")
            print(f"Hint: {q.hint}")
            print(f"\n{'-'*60}\n")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
