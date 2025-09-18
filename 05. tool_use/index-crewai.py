import os
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

@tool("Stock Price Lookup Tool")
def get_stock_price(ticker: str) -> float:
    """
    Fetches the latest simulated stock price for a given stock ticker
    symbol.
    Returns the price as a float. Raises a ValueError if the ticker is
    not found.
    """
    simulated_prices = {
    "AAPL": 178.15,
    "GOOGL": 1750.30,
    "MSFT": 425.50,
    }
    price = simulated_prices.get(ticker.upper())
    if price is not None:
     return price
    else:
        # Raising a specific error is better than returning a string.
        # The agent is equipped to handle exceptions and can decide on the next action.
        raise ValueError(f"Simulated price for ticker '{ticker.upper()}' not found.")

# Configure Gemini LLM
def setup_gemini_llm():
    """Setup and return a Gemini LLM instance for CrewAI"""
    
    if not api_key:
        raise ValueError("Google Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
    
    return LLM(
        model="gemini/gemini-1.5-flash",  # or "gemini/gemini-1.5-pro" for more advanced tasks
        api_key=api_key
    )

# Initialize the LLM
gemini_llm = setup_gemini_llm()

financial_analyst_agent = Agent(
    role='Senior Financial Analyst',
    goal='Analyze stock data using provided tools and report key prices.',
    backstory="You are an experienced financial analyst adept at using data sources to find stock information. You provide clear, direct answers.",
    verbose=True,
    tools=[get_stock_price],
    llm=gemini_llm,  # Use Gemini as the LLM backend
    # Allowing delegation can be useful, but is not necessary for this simple task.
    allow_delegation=False,
)

analyze_aapl_task = Task(
    description=(
        "What is the current simulated stock price for Apple (ticker: AAPL)? "
        "Use the 'Stock Price Lookup Tool' to find it. "
        "If the ticker is not found, you must report that you were unable to retrieve the price."
    ),
    expected_output=(
        "A single, clear sentence stating the simulated stock price for AAPL. "
        "For example: 'The simulated stock price for AAPL is $178.15.' "
        "If the price cannot be found, state that clearly."
),
agent=financial_analyst_agent,
)

financial_crew = Crew(
    agents=[financial_analyst_agent],
    tasks=[analyze_aapl_task],
    verbose=True # Set to False for less detailed logs in production
)

def main():
    """Main function to run the crew."""
    try:
        # Check for API key before starting to avoid runtime errors.
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable is not set.")
            print("Please set your Google Gemini API key: export GOOGLE_API_KEY='your-api-key-here'")
            return
            
        print("\n## Starting the Financial Crew with Gemini LLM...")
        print("---------------------------------")
        # The kickoff method starts the execution.
        result = financial_crew.kickoff()
        print("\n---------------------------------")
        print("## Crew execution finished.")
        print("\nFinal Result:\n", result)
    except Exception as e:
        print(f"Error running the crew: {e}")
        print("Make sure you have set the GOOGLE_API_KEY environment variable with a valid Gemini API key.")

if __name__ == "__main__":
    main()