from google.adk.agents import Agent, ParallelAgent
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

weather_fetcher = Agent(
    name="weather_fetcher",
    model="gemini-2.0-flash-exp",
    instruction="Fetch the weather for the given location and return only the weather report.",
    output_key="weather_data" # The result will be stored in session.state["weather_data"]
)
news_fetcher = Agent(
    name="news_fetcher",
    model="gemini-2.0-flash-exp",
    instruction="Fetch the top news story for the given topic and return only that story.",
    output_key="news_data" # The result will be stored in session.state["news_data"]
)
# Create the ParallelAgent to orchestrate the sub-agents
data_gatherer = ParallelAgent(
    name="data_gatherer",
    sub_agents=[
    weather_fetcher,
        news_fetcher
    ]
)

async def call_agent(query):
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=data_gatherer, app_name=APP_NAME, session_service=session_service)

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
asyncio.run(call_agent("London"))