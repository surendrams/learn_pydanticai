from pydantic_ai import Agent, RunContext
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# 2. Initialize the Agent
# We tell it which model to use and what the result type should be.
agent = Agent(
    model='gemini-3-flash-preview'
)

@agent.tool
def calculate_discount(ctx: RunContext[None], original_price: float, discount_percent: float) -> str:
    """Calculates the final price after a discount.
    
    Args:
        original_price: The starting price of the item.
        discount_percent: The percentage to take off (e.g., 20 for 20%).
    """
    final_price = original_price * (1 - discount_percent / 100)
    return f"The discounted price is ${final_price:.2f}"

# Running the agent
result = agent.run_sync("I found a pair of shoes for $120 with a 15% discount. How much are they?")
print(result.output)