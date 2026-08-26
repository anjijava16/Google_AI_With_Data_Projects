import os
from google import genai
from google.genai import types

# 1. Define your tools (Python functions)
# The model reads the docstring and type hints to understand when and how to use them.
def get_current_stock_price(ticker: str) -> str:
    """
    Retrieves the current stock price for a given ticker symbol.
    
    Args:
        ticker: The stock ticker symbol (e.g., 'GOOG', 'AAPL').
    """
    # Mock implementation - replace with an actual API call if needed
    mock_database = {"GOOG": "$180.50", "AAPL": "$175.20", "MSFT": "$420.10"}
    price = mock_database.get(ticker.upper(), "unknown")
    return f"The current price of {ticker.upper()} is {price}."

def calculate_investment_value(shares: int, price_str: str) -> str:
    """
    Calculates the total value of an investment based on share count and price.
    
    Args:
        shares: The number of shares owned.
        price_str: The price per share as a string (e.g., '$180.50').
    """
    try:
        # Clean the price string to do math
        clean_price = float(price_str.replace('$', '').strip())
        total = shares * clean_price
        return f"Total portfolio value: ${total:,.2f}"
    except Exception as e:
        return f"Could not calculate value: {str(e)}"


# 2. Initialize the Gemini client
# It automatically picks up GEMINI_API_KEY from your environment variables
client = genai.Client()

# 3. Create a chat session configured with your tools
# The model will look at this list and decide which tools to execute automatically.
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        tools=[get_current_stock_price, calculate_investment_value],
        temperature=0.2, # Lower temperature makes the agent more deterministic
    )
)

# 4. Prompt the agent with a task that requires using BOTH tools sequentially
prompt = (
    "I own 50 shares of GOOG. Find the current stock price using your tools, "
    "and then calculate the total value of my investment."
)

print(f"User: {prompt}\n")
print("--- Agent Processing (Automatic Function Calling) ---")

# The SDK executes the function loop in the background and returns the final answer
response = chat.send_message(prompt)

print("Agent Final Response:")
print(response.text)
