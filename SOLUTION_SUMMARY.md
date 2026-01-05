# PydanticAI Issue Resolution

## Issues Encountered

### 1. Original Issue: Output Validation Errors
**Error**: `pydantic_ai.exceptions.UnexpectedModelBehavior: Exceeded maximum retries (3) for output validation`

**Root Cause**: Google Gemini was returning question text as plain strings instead of structured JSON objects.

```
Expected: {"question_type": "multiple_choice", "question_text": "...", ...}
Actual: "Solve the system of equations..."
```

**Why**: Not all models handle structured output equally well. Gemini 2.0 Flash struggled with the complex nested Pydantic schema.

### 2. Connection Errors
**Error**:
- With `trust_env=False`: DNS resolution fails
- With `trust_env=True`: Proxy returns "403 Forbidden"

**Root Cause**: Your network environment requires a proxy for DNS resolution, but the proxy blocks connections to OpenRouter.ai

## Solutions

### Solution 1: Use OpenAI Directly (Recommended)
- File: `main_openai_direct.py`
- Add to `.env`: `OPENAI_API_KEY=sk-...`
- Uses: GPT-4 or GPT-3.5-turbo
- Pro: Excellent structured output support
- Pro: Generally accessible through proxies

### Solution 2: Use Claude Directly
- File: `main_claude_direct.py`
- Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`
- Uses: Claude 3.5 Sonnet
- Pro: Best-in-class structured output support
- Pro: May work through your proxy

### Solution 3: Fix Proxy/Network (For OpenRouter)
If you want to keep using OpenRouter:
1. Configure your proxy to allow openrouter.ai
2. Use a VPN that bypasses the proxy
3. Switch to a different network

## Updated .env File

Add one of these to your `.env` file:

```bash
# For OpenAI
OPENAI_API_KEY=your-openai-key-here

# OR for Claude
ANTHROPIC_API_KEY=your-anthropic-key-here

# Keep existing OpenRouter config (if you fix the proxy)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Files Created

1. `main_02.py` - Updated with Claude via OpenRouter (requires proxy fix)
2. `main_03.py` - Enhanced version with better error handling
3. `main_openai_direct.py` - Uses OpenAI API directly (RECOMMENDED)
4. `main_claude_direct.py` - Uses Claude API directly
5. `test_connection.py` - Network diagnostic tool

## Model Comparison for Structured Output

| Model | Structured Output Quality | Access |
|-------|---------------------------|--------|
| Claude 3.5 Sonnet | Excellent ⭐⭐⭐⭐⭐ | Direct API |
| GPT-4 | Excellent ⭐⭐⭐⭐⭐ | Direct API |
| GPT-3.5-turbo | Very Good ⭐⭐⭐⭐ | Direct API |
| Gemini 2.0 Flash | Fair ⭐⭐ | Via OpenRouter (blocked) |

## Recommended Next Steps

1. Get an API key from OpenAI or Anthropic
2. Add it to your `.env` file
3. Run `uv run main_openai_direct.py` or `uv run main_claude_direct.py`
4. The validation errors should be resolved
