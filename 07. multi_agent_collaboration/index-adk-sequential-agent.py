from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from google.adk.events import Event
from typing import AsyncGenerator
from google.genai import types
import nest_asyncio
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Define variables required for Session setup and Agent execution
APP_NAME="Google Search_agent"
USER_ID="user1234"
SESSION_ID="1234"

# This agent's output will be saved to session.state["data"]
step1 = Agent(
    name="Step1_Fetch", 
    instruction="Process the user's query and do calculations. Your response (calculated value only) will be saved for the next agent to analyze.",
    output_key="data", 
    model="gemini-2.0-flash-exp"
)
# This agent will use the data from the previous step.
# We instruct it on how to find and use this data.
step2 = Agent(
    name="Step2_Process",
    instruction="You are the second step in a pipeline. Double up session['data'].",
    model="gemini-2.0-flash-exp"
)
pipeline = SequentialAgent(
    name="MyPipeline",
    sub_agents=[step1, step2]
)

async def call_agent(query):
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=pipeline, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts') and event.content.parts:
                response = event.content.parts[0].text
                author = getattr(event, 'author', 'Unknown')
                print(f"{author}: {response}")
                print("---")

nest_asyncio.apply()
asyncio.run(call_agent("Tell me what is 5 + 5"))