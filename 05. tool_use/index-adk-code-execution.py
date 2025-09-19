from google.adk.agents import Agent as ADKAgent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import google_search
from google.genai import types
import nest_asyncio
import asyncio
from typing import List
from dotenv import load_dotenv
load_dotenv()

# Define variables required for Session setup and Agent execution
APP_NAME="Google Search_agent"
USER_ID="user1234"
SESSION_ID="1234"

code_agent = LlmAgent(
    name="calculator_agent",
    model="gemini-2.0-flash",
    code_executor=BuiltInCodeExecutor(),
    description="Executes python code to do calculations",
    instruction="""
You are a calculator agent. When given a mathematical expression, you should evaluate it and return the result.
Return only the final numeerical result as plaint text without markdown or code blocks"""
)

async def call_agent_async(query):
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=code_agent, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "No final text response captured."
    
    try:
        # Use run_async
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            print(f"Event ID: {event.id}, Author: {event.author}")
            # --- Check for specific parts FIRST ---
            # has_specific_part = False
            if event.content and event.content.parts and event.is_final_response():
                for part in event.content.parts:  # Iterate through all parts
                    if part.executable_code:
                        # Access the actual code string via .code
                        print(f" Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```")
                        has_specific_part = True
                    elif part.code_execution_result:
                        # Access outcome and output correctly
                        has_specific_part = True
        # Also print any text parts found in any event for debugging
            elif part.text and not part.text.isspace():
                print(f" Text: '{part.text.strip()}'")
        # Do not set has_specific_part=True here, as we want the final response logic below
        # --- Check for final response AFTER specific parts ---
        text_parts = [part.text for part in event.content.parts if part.text]
        final_result = "".join(text_parts)
        print(f"==> Final Agent Response: {final_result}")
    except Exception as e:
        print(f"ERROR during agent run: {e}")

async def main():
    await call_agent_async("Calculate the value of (5 + 7) * 3")
    await call_agent_async("What is 10 factorial?")

nest_asyncio.apply()
asyncio.run(main())