from google.adk.agents import Agent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from google.adk.tools import agent_tool
from google.genai import types
import nest_asyncio
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Define variables required for Session setup and Agent execution
APP_NAME="Google Search_agent"
USER_ID="user1234"
SESSION_ID="1234"

def generate_image(prompt: str) -> dict:
    print(f"TOOL: Generating image for prompt: '{prompt}'")
    # In a real implementation, this would call an image generation API.
    # For this example, we return mock image data.
    mock_image_bytes = b"mock_image_data_for_a_cat_wearing_a_hat"
    return {
    "status": "success",
    # The tool returns the raw bytes, the agent will handle the Part creation.
    "image_bytes": mock_image_bytes,
    "mime_type": "image/png"
    }

image_generator_agent = LlmAgent(
    name="ImageGen",
    model="gemini-2.0-flash",
    description="Generates an image based on a detailed text prompt.",
    instruction=(
    "You are an image generation specialist. Your task is to take the user's request "
    "and use the `generate_image` tool to create the image. "
    "The user's entire request should be used as the 'prompt' argument for the tool. "
    "After the tool returns the image bytes, you MUST output the image."
    ),
tools=[generate_image]
)

image_tool = agent_tool.AgentTool(
agent=image_generator_agent,
# description="Use this tool to generate an image. The input should be a descriptive prompt of the desired image."
)

# Create the ParallelAgent to orchestrate the sub-agents
artist_agent = LlmAgent(
name="Artist",
model="gemini-2.0-flash",
instruction=(
"You are a creative artist. First, invent a creative and descriptive prompt for an image. "
"Then, use the `ImageGen` tool to generate the image using your prompt."
),
tools=[image_tool]
)

async def call_agent(query):
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=artist_agent, app_name=APP_NAME, session_service=session_service)

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
asyncio.run(call_agent(""))