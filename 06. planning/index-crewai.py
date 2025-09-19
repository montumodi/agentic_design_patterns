import os
from crewai import Agent, Task, Crew, LLM, Process
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

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

planner_writer_agent = Agent(
    role='Article Planner and Writer',
    goal='Plan and then write a concise, engaging summary on a specified topic.',
    backstory=(
    'You are an expert technical writer and content strategist. '
    'Your strength lies in creating a clear, actionable plan before writing, '
    'ensuring the final summary is both informative and easy to digest.'
    ),
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm # Assign the specific LLM to the agent
)

topic = "The importance of Reinforcement Learning in AI"

high_level_task = Task(
    description=(
        f"1. Create a bullet-point plan for a summary on the topic:'{topic}'.\n"
        f"2. Write the summary based on your plan, keeping it around 200 words."
    ),
    expected_output=(
       "A final report containing two distinct sections:\n\n"
        "### Plan\n"
        "- A bulleted list outlining the main points of the summary.\n\n"
        "### Summary\n"
        "- A concise and well-structured summary of the topic."
),
agent=planner_writer_agent,
)

crew = Crew(
    agents=[planner_writer_agent],
    tasks=[high_level_task],
    process=Process.sequential,
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
        result = crew.kickoff()
        print("\n---------------------------------")
        print("## Crew execution finished.")
        print("\nFinal Result:\n", result)
    except Exception as e:
        print(f"Error running the crew: {e}")
        print("Make sure you have set the GOOGLE_API_KEY environment variable with a valid Gemini API key.")

if __name__ == "__main__":
    main()