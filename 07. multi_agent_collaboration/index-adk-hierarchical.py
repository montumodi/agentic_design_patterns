from google.adk.agents import LlmAgent, BaseAgent
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

class TaskExecutor(BaseAgent):
    name:str = "TaskExecutor"
    description:str = "Executes a pre defined task."

    async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        yield Event(author=self.name, content=f"Task finished successfully.")

greeter = LlmAgent(
    name="Greeter",
    model="gemini-2.0-flash-exp",
    instruction="You are a friendly greeter."
)

task_doer = TaskExecutor()

coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash-exp",
    description="A coordinator that greet users and execute tasks",
    instruction="When asked to greet, delegate to the greeter. When asked to perform a task, delegate to the TaskExecutor.",
    sub_agents=[greeter, task_doer]
)

assert greeter.parent_agent == coordinator
assert task_doer.parent_agent == coordinator
print("Agent hierarchy created successfully.")

async def call_agent(query):
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=coordinator, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print(final_response)

nest_asyncio.apply()
asyncio.run(call_agent("good morning"))