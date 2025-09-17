import uuid
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_MODEL = "gemini-2.0-flash"

generator = LlmAgent(
    name="DraftWriter",
    description="A language model that can generate text based on a prompt.",
    instruction="Write a short, informative paragraph about the user's subject",
    output_key="draft_text",
    model=GEMINI_MODEL
    
)

reviewer = LlmAgent(
    name="FactChecker",
    description="A language model that can review and fact-check text.",
    model=GEMINI_MODEL,
    instruction="""
You are a meticulous fact-checker.
1. Read the text provided in the state key 'draft_text'.
2. Carefully verify the factual accuracy of all claims.
3. Your final output must be a dictionary containing two keys:
- "status": A string, either "ACCURATE" or "INACCURATE".
- "reasoning": A string providing a clear explanation for your
status, citing specific issues if any are found.
""",
    output_key="review_output"
)

review_pipeline = SequentialAgent(
    name="ReviewPipeline",
    sub_agents=[generator, reviewer]
)

import asyncio

async def main():
  runner = InMemoryRunner(app_name="ParallelizationApp", agent=review_pipeline)
  user_id = "user234"
  session_id = str(uuid.uuid4())
  await runner.session_service.create_session(
        app_name=runner.app_name, user_id=user_id, session_id=session_id
    )

  result_gen = runner.run(
      user_id=user_id,
      session_id=session_id,
      new_message=types.Content(
            role='user',
            parts=[types.Part(text="History of cricket")],
        ),

  )
  for result in result_gen:
    print(result)

if __name__ == "__main__":
  asyncio.run(main())

