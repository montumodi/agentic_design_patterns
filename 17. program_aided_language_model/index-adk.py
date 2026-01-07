from google.adk.tools import agent_tool
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor

from google.genai import types
from typing import Optional
from dotenv import load_dotenv
import uuid
from google.adk.runners import InMemoryRunner

# Load environment variables from .env file
load_dotenv()

search_agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a helpful assistant that uses Google Search to find information.
    When given a query, use the google_search tool to find relevant information.
    Provide concise and accurate answers based on the search results.
    """,
    tools=[google_search]
)

coding_agent = Agent(
    name="coding_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a coding assistant that can write and execute Python code.
    When given a programming task, use the BuiltInCodeExecutor tool to write and run Python code.
    Provide clear and correct code snippets based on the user's requirements.
    """,
    tools=[BuiltInCodeExecutor]
)

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a root agent that delegates tasks to specialized agents.
    When given a request, determine whether it requires information retrieval or coding.
    If it requires information retrieval, delegate to the search_agent.
    If it requires coding, delegate to the coding_agent.
    Combine the results from the specialized agents to provide a comprehensive response.
    """,
    tools=[agent_tool.AgentTool(agent=search_agent), agent_tool.AgentTool(agent=coding_agent)]
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
    runner = InMemoryRunner(root_agent)
    request = "My computer is showing -100 percent CPU usage. Can you help me it seems like a very complex issue to me? Please escalate to human"
    response = await run_coordinator(runner, request)
    print(f"Response: {response}")

    if hasattr(runner, "shutdown"):
        await runner.shutdown()
    elif hasattr(runner, "close"):
        await runner.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())