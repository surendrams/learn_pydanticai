# PydanticAI Learning Project

A comprehensive learning repository demonstrating various features and capabilities of [PydanticAI](https://github.com/pydantic/pydantic-ai), an agent framework built on top of Pydantic for building production-grade LLM applications.

## Overview

This project explores PydanticAI's features through practical examples, including structured output generation, multi-provider support, agent tools, system prompts, dependency injection, and observability with Logfire.

## Features Demonstrated

- **Multiple LLM Provider Integration**
  - OpenAI via OpenRouter
  - Google Gemini (direct and via OpenRouter)
  - Anthropic Claude (direct and via OpenRouter)

- **Structured Output Generation**
  - Type-safe responses using Pydantic models
  - Complex nested schemas (e.g., question banks with options, hints, explanations)

- **Agent Capabilities**
  - Custom tools and function calling
  - Dynamic and static system prompts
  - Dependency injection
  - Output validation and retries

- **Observability**
  - Logfire integration for monitoring and debugging

- **Database Integration**
  - MongoDB async client with Motor
  - Collections for sessions, messages, student progress, quizzes, and curriculum

## Project Structure

```
.
├── main.py                    # Basic hello world example
├── main_01.py                 # OpenRouter integration with structured output
├── main_02.py                 # Advanced question generation with Logfire
├── main_03.py                 # Google Gemini integration
├── main_dependencies.py       # Dependency injection example
├── main_prompts.py            # Dynamic system prompts demonstration
├── main_tool.py               # Agent tools example (discount calculator)
├── try_anthropic.py           # Direct Anthropic API usage
├── database.py                # MongoDB connection and collection management
├── test_connection.py         # Network diagnostics utility
└── pyproject.toml             # Project dependencies
```

## Prerequisites

- Python 3.13+
- MongoDB instance (for database examples)
- API keys for at least one LLM provider:
  - OpenRouter API key
  - Google AI API key
  - Anthropic API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pydanticai
```

2. Install dependencies using uv:
```bash
uv sync
```

Or with pip:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# OpenRouter (supports multiple models)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Google AI
GOOGLE_API_KEY=AIza...
GOOGLE_MODEL=gemini-3-flash-preview

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

## Running Examples

### Basic Example
```bash
uv run main.py
```

### OpenRouter with Structured Output
```bash
uv run main_01.py
```

### Question Bank Generation (with Logfire)
```bash
uv run main_02.py
```

### Google Gemini Direct
```bash
uv run main_03.py
```

### Agent Tools
```bash
uv run main_tool.py
```

### Dynamic System Prompts
```bash
uv run main_prompts.py
```

### Dependency Injection
```bash
uv run main_dependencies.py
```

### Anthropic Direct API
```bash
uv run try_anthropic.py
```

## Key Examples

### 1. Structured Output with Pydantic Models

The project demonstrates generating structured STEM questions with proper type safety:


### 2. Agent Tools

Custom tools allow agents to perform specific calculations or operations:

```python
@agent.tool
def calculate_discount(ctx: RunContext[None],
                      original_price: float,
                      discount_percent: float) -> str:
    final_price = original_price * (1 - discount_percent / 100)
    return f"The discounted price is ${final_price:.2f}"
```

See `main_tool.py` for the complete example.

### 3. Dynamic System Prompts

System prompts can be dynamic and context-aware:

```python
@agent.system_prompt
def current_date_instruction() -> str:
    return f"Today's date is {date.today()}."

@agent.system_prompt
def personalize_prompt(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps}."
```

See `main_prompts.py` for the complete example.

### 4. Dependency Injection

Pass runtime dependencies to your agents:

```python
@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent('gemini-3-flash-preview', deps_type=MyDeps)
```

## Observability

The project uses [Logfire](https://pydantic.dev/logfire) for observability:

```python
import logfire
logfire.configure()
logfire.instrument_pydantic_ai()
```

Use the diagnostic tool:
```bash
uv run test_connection.py
```

## Dependencies

Core dependencies:
- `pydantic-ai>=1.39.0` - Main framework
- `google-adk>=1.14.1` - Google AI integration
- `logfire>=4.16.0` - Observability
- `motor>=3.7.1` - Async MongoDB driver
- `python-dotenv>=1.2.1` - Environment management

Development:
- `ruff>=0.14.10` - Linting and formatting
- `isort>=7.0.0` - Import sorting

## Learning Resources

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Logfire Documentation](https://pydantic.dev/logfire)

## License

This is a learning project for educational purposes.

## Notes

- The project includes examples of handling network proxy configurations
- API keys in `.env` should never be committed to version control
- MongoDB connection string defaults to `mongodb://localhost:27017`
- Most examples use async/await patterns for better performance
