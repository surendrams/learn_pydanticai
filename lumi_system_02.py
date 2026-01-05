import os
import asyncio

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from database import MongoDB, get_questions_collection, get_curriculum_collection

load_dotenv(find_dotenv())

# --- 1. DATA MODELS ---
class Grade(str, Enum):
    SIXTH = "6"
    SEVENTH = "7"
    EIGHTH = "8"
    NINTH = "9"
    TENGTH = "10"
    ELEVENTH = "11"
    TWELEVTH = "12"
    OTHERS = "99"

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
    correct_option: str = Field(description="The ID of the correct answer(s), e.g., 'A,C' for 'multiple_choice'; 'B' for 'single_select'; 'true' for 'true_false' ")
    explanation: str = Field(description="MAX 3 LINES. Explain the logic clearly.")
    hint: str = Field(description="MAX 3 LINES. Give a helpful nudge.")
    
class QuestionBank(BaseModel):
    questions: List[QuestionDocument] = Field(
        default_factory=list,
        description="List of question documents"
    )

class Question(BaseModel):
    question_id: str
    grade: Grade = Field(description="Grade level of the question")
    subject: str
    topic: str
    subtopic: Optional[str] = None
    difficulty: QuestionDifficulty
    question_type: QuestionType
    question_text: str = Field(description="The STEM question. Wrap math in $. Use \\\\ for LaTeX commands.")
    options: List[QuestionOption]
    correct_option: str = Field(description="The ID of the correct answer(s), e.g., 'A' or 'A,C'")
    explanation: str = Field(description="MAX 3 LINES. Explain the logic clearly.")
    hint: str = Field(description="MAX 3 LINES. Give a helpful nudge.")
    created_by: str  # agent or teacher_id
    created_at: datetime = Field(default_factory=datetime.now)


class ValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None

@dataclass
class UserRequirements:
    grade: Grade = Grade.SIXTH
    subject: str = ""
    reference: str = ""
    topic: str = ""
    subtopic: Optional[str] = None
    difficulty: QuestionDifficulty = QuestionDifficulty.BEGINNER
    number_of_questions: int = 1


# --- 2. AGENT & DB SETUP ---

google_provider = GoogleProvider(api_key=os.getenv('GOOGLE_API_KEY'))
model = GoogleModel(os.getenv('GOOGLE_MODEL', default='gemini-3-flash-preview'), provider=google_provider)

# MongoDB will be initialized in the async main function

# --- 3. AGENT DEFINITIONS ---

extractor_agent = Agent(
    model=model,
    deps_type=UserRequirements,
    system_prompt="Extract question requirements (grade, subject, number_of_questions). Use 'update_requirements' tool."
)

@extractor_agent.tool
async def update_requirements(ctx: RunContext[UserRequirements], grade: Grade, subject: str, reference: str, topic: str,
                            subtopic: str, difficulty: QuestionDifficulty, number_of_questions: int):
    ctx.deps.grade = grade
    ctx.deps.subject = subject
    ctx.deps.reference = reference
    ctx.deps.topic = topic
    ctx.deps.subtopic = subtopic
    ctx.deps.difficulty = difficulty
    ctx.deps.number_of_questions = number_of_questions

    # Fetch reference value from database for the given grade and subject
    curriculum_db = get_curriculum_collection()
    curriculum_doc = await curriculum_db.find_one(
        {"grade": grade, "subject": subject},
        {"reference": 1, "_id": 0}
    )

    # Update reference if found in database
    if curriculum_doc and "reference" in curriculum_doc:
        ctx.deps.reference = curriculum_doc["reference"]

    return "Requirements updated."
    

tutor_agent = Agent(
    model=model,
    deps_type=UserRequirements,
    output_type=QuestionBank,
    system_prompt="You are Middle and High school Tutor. Generate high-quality questions with LaTeX."
)

@tutor_agent.system_prompt
def add_context(ctx: RunContext[UserRequirements]) -> str:
    print(f"Create a {ctx.deps.subject} questions on {ctx.deps.topic} and {ctx.deps.subtopic} for {ctx.deps.grade.value} level with {ctx.deps.difficulty.value} difficulty level {ctx.deps.number_of_questions} questions. Refer {ctx.deps.reference}")
    return f"Create a {ctx.deps.subject} questions on {ctx.deps.topic} and {ctx.deps.subtopic} for {ctx.deps.grade.value} level with {ctx.deps.difficulty.value} difficulty level {ctx.deps.number_of_questions} questions. Refer {ctx.deps.reference}"

validator_agent = Agent(
    model,
    output_type=ValidationResult,
    system_prompt="Review the question for math accuracy and LaTeX syntax."
)

@tutor_agent.output_validator
async def validate_question_rigor(ctx: RunContext[UserRequirements], question: QuestionBank) -> QuestionBank:
    validation = await validator_agent.run(f"Review this: {question.model_dump_json()}")
    if not validation.output.is_valid:
        raise ModelRetry(f"Validation failed: {validation.output.error_message}")
    return question

# --- 4. THE MAIN ORCHESTRATOR WITH PERSISTENCE ---

async def run_lumi_flow(user_input: str):
    shared_deps = UserRequirements()
    
    # 1. Extraction
    await extractor_agent.run(user_input, deps=shared_deps)

    # 2. Generation & Validation (Managed by PydanticAI)
    result = await tutor_agent.run("Generate the question now.", deps=shared_deps)
    final_question = result.output

    # 3. Database Save
    print("💾 Saving validated question to MongoDB...")
    question_data = final_question.model_dump()
    # print(json.dumps(question_data, indent=2))

    question_collection = get_questions_collection()
    # Get Max question_id 
    # Aggregation pipeline to find max number with filter
    pipeline = [
        {
            '$match': {
                'grade': shared_deps.grade.value,
                'subject': shared_deps.subject
            }
        },
        {
            '$project': {
                'question_id': 1,
                'numeric_part': {
                    '$toInt': {
                        '$arrayElemAt': [
                            {'$split': ['$question_id', '_']},
                            -1
                        ]
                    }
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'max_number': {'$max': '$numeric_part'}
            }
        }
    ]

    result = await question_collection.aggregate(pipeline).to_list(length=None)
    max_number = result[0]['max_number'] if result else 1

    print(f"Maximum number: {max_number}")
    max_number += 1

    for generated_question in question_data["questions"]:
        question_document = Question(
            question_id = f"GR_{shared_deps.grade.value}_{shared_deps.subject.replace(" ", "")}_{max_number:06d}",
            grade=shared_deps.grade,
            subject=shared_deps.subject,
            topic=shared_deps.topic,
            subtopic=shared_deps.subtopic,
            difficulty=shared_deps.difficulty,
            question_type=generated_question["question_type"],
            question_text=generated_question["question_text"],
            options=[QuestionOption(**opt) for opt in generated_question["options"]],
            correct_option=generated_question["correct_option"],
            explanation=generated_question["explanation"],
            hint=generated_question["hint"],
            created_by="surendra",
            created_at=datetime.now()
        )
        question_data_to_save = question_document.model_dump()
        insert_result = await question_collection.insert_one(question_data_to_save)
        max_number += 1
        print(f"✅ Question saved successfully with ID: {insert_result.inserted_id}")
    
    return final_question

if __name__ == "__main__":
    async def main():
        # Connect to MongoDB first
        await MongoDB.connect_db()

        try:
            prompt = "I need 2 hard Algebra 1 questions about polynomials for a 9th grader."
            question = await run_lumi_flow(prompt)
            print(f"\nSee above results")
        finally:
            # Close database connection
            await MongoDB.close_db()

    asyncio.run(main())
