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

researcher = Agent(
    role='Senior Research Analyst',
    goal='Find and summarize the latest trends in Agentic AI.',
    backstory="You are an experienced research analyst with a knack for identifying key trends and synthesizing information.",
    verbose=True,
    llm=gemini_llm,  # Use Gemini as the LLM backend
    # Allowing delegation can be useful, but is not necessary for this simple task.
    allow_delegation=False,
)

writer = Agent(
    role='Technical Content Writer',
    goal='Write a clear and engaging blog post based on research findings.',
    backstory="You are a skilled writer who can translate complex technical topics into accessible content.",
    verbose=True,
    llm=gemini_llm,  # Use Gemini as the LLM backend
    # Allowing delegation can be useful, but is not necessary for this simple task.
    allow_delegation=False,
)

research_task = Task(
    description=(
        "Research the top 3 emerging trends in Agentic AI in 2024-2025. Focus on practical applications and potential impact."
    ),
    expected_output=(
        "A detailed summary of the top 3 Agentic AI trends,including key points and sources."
),
agent=researcher,
)

writing_task = Task(
    description=(
        "Write a 500-word blog post based on the research findings. The post should be engaging and easy for a general audience to understand."
    ),
    expected_output=(
        "A complete 500-word blog post about the latest Agentic AI trends."
),
agent=writer,
context=[research_task]
)
    
blog_creation_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    llm=gemini_llm,
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
        result = blog_creation_crew.kickoff()
        print("\n---------------------------------")
        print("## Crew execution finished.")
        print("\nFinal Result:\n", result)
    except Exception as e:
        print(f"Error running the crew: {e}")
        print("Make sure you have set the GOOGLE_API_KEY environment variable with a valid Gemini API key.")

if __name__ == "__main__":
    main()