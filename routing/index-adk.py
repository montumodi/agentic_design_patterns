import uuid
from typing import Dict, Any, Optional
import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool
from google.genai import types
from google.adk.events import Event
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Define simulated sub agent handlers
def booking_handler(request: str) -> str:
    """Simulates the Booking Agent handling a request."""
    print("\n--- DELEGATING TO BOOKING HANDLER ---")
    return f"Booking Handler processed request: '{request}'. Result:Simulated booking action."

def info_handler(request: str) -> str:
    """Simulates the Info Agent handling a request."""
    print("\n--- DELEGATING TO INFO HANDLER ---")
    return f"Info Handler processed request: '{request}'. Result:Simulated info action."

def unclear_handler(request: str) -> str:
    """Simulates the Unclear Agent handling a request."""
    print("\n--- DELEGATING TO UNCLEAR HANDLER ---")
    return f"Coordinator could not delegate request: '{request}'. Please clarify"

# Create tools from function
booking_tool = FunctionTool(booking_handler)
info_tool = FunctionTool(info_handler)

# Define specialized sub agents equipped with thier resespective tools
booking_agent = Agent(
    name="Booker",
    model="gemini-2.0-flash",
    tools=[booking_tool],
    description="A specialized agent that handles all flight and hotel booking requests by calling the booking tool.",
)

info_agent = Agent(
    name="Info",
    model="gemini-2.0-flash",
    tools=[info_tool],
    description="A specialized agent that provides general information and answers user questions by calling the info tool.",
)

# Define the parent agent with explicit delegation instructions

coordinator = Agent(
    name="Coordinator",
    model="gemini-2.0-flash",
    instruction=(
        """You are the main coordinator. Your only task is to analyze
        incoming user requests and delegate them to the appropriate specialist agent.
        Do not try to answer the user directly.
        - For any requests related to booking flights or hotels, delegate to the 'Booker' agent.
        - For all other general information questions, delegate to the 'Info' agent."""
    ),
    sub_agents=[booking_agent, info_agent],
    description="A specialized agent that coordinates requests and delegates them to the appropriate sub-agent."
)

async def run_coordinator(runner: InMemoryRunner, request: str):
    user_id = "user234"
    session_id = str(uuid.uuid4())
    await runner.session_service.create_session(
        app_name=runner.app_name, user_id=user_id, session_id=session_id
    )

    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role='user',
            parts=[types.Part(text=request)]
        ),
    )

    for event in events:
        if event.is_final_response() and event.content:
            # Try to get text from event.content.text or from parts
            if getattr(event.content, 'text', None):
                return event.content.text
            text_parts = [part.text for part in getattr(event.content, 'parts', []) if getattr(part, 'text', None)]
            if text_parts:
                return " ".join(text_parts)
    return "No response received."
    
async def main():
    runner = InMemoryRunner(coordinator)
    request = "I want to taste idly"
    response = await run_coordinator(runner, request)
    print(f"Response: {response}")

    if hasattr(runner, "shutdown"):
        await runner.shutdown()
    elif hasattr(runner, "close"):
        await runner.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())