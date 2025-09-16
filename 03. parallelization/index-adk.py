import uuid
import os
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_MODEL = "gemini-2.0-flash"

# Define researcher sub agent (to run in parallel)
# Reasercher 1: Renewable Energy

researcher_agent_1 = LlmAgent(
    name="RenewableEnergyResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI research assistant speciliazing in energy.
      Research the latest developements in 'renewable energy sources'.
        Use the google search tool provided.
          Summarize your key findings concisely (1-2 sentences).
          Output *only* the summary""",
    tools=[google_search],
    description="This agent specializes in renewable energy research.",
    output_key="renewable_energy_result"
)

# Researcher 2: Electric Vehicles

researcher_agent_2 = LlmAgent(
    name="ElectricVehiclesResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI research assistant speciliazing in transportation.
      Research the latest developements in 'electric vehicles technology'.
        Use the google search tool provided.
          Summarize your key findings concisely (1-2 sentences).
          Output *only* the summary""",
    tools=[google_search],
    description="This agent specializes in electric vehicles research.",
    output_key="ev_technology_result"
)

# Researcher 3: Carbon Capture

researcher_agent_3 = LlmAgent(
    name="CarbonCaptureResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI research assistant speciliazing in climate solutions.
      Research the latest developements in 'carbon capture methods'.
        Use the google search tool provided.
          Summarize your key findings concisely (1-2 sentences).
          Output *only* the summary""",
    tools=[google_search],
    description="This agent specializes in carbon capture research.",
    output_key="carbon_capture_result"
)

# Create the parallel agent to run all researchers in parallel
parallel_researcher_agent = ParallelAgent(
    name="ParallelWebResearcherAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
    description="This agent runs multiple researchers in parallel."
)

# Define the merger agent
merger_agent = LlmAgent(
    name="SynthesisAgent",
    model=GEMINI_MODEL,
    instruction="""You are an AI assistant responsible for combining research findings in to structured report.
      Your primary task is to synthesize the following research summaries, clearly
      attributing findings to their source areas. Structure your response using headings for each topic.
      Ensure the report is coherent and integrates the key points smoothly.
        **Crucially: Your entire response MUST be grounded *exclusively* on the 
        informatio provided in the 'Input Summaries' below. DO NOT add any external knowledge, facts, or details not present
        in theese specific summaries.**
        
        **Input Summaries:**
* **Renewable Energy:**
{renewable_energy_result}
* **Electric Vehicles:**
{ev_technology_result}
* **Carbon Capture:**
{carbon_capture_result}
**Output Format:**
## Summary of Recent Sustainable Technology Advancements
### Renewable Energy Findings
(Based on RenewableEnergyResearcher's findings)
[Synthesize and elaborate *only* on the renewable energy input
summary provided above.]
### Electric Vehicle Findings
(Based on EVResearcher's findings)
[Synthesize and elaborate *only* on the EV input summary provided
above.]
### Carbon Capture Findings
(Based on CarbonCaptureResearcher's findings)
[Synthesize and elaborate *only* on the carbon capture input summary
provided above.]
### Overall Conclusion
[Provide a brief (1-2 sentence) concluding statement that connects
*only* the findings presented above.]
Output *only* the structured report following this format. Do not
include introductory or concluding phrases outside this structure,
and strictly adhere to using only the provided input summary content.
""",
    description="This agent merges the results from multiple researchers.",
)

# Define main agent

sequential_pipeline_agent = SequentialAgent(
    name="SequentialPipelineAgent",
    sub_agents=[parallel_researcher_agent, merger_agent],
    description="This agent runs a sequential pipeline of agents."
)

root_agent = sequential_pipeline_agent

# --- Async main for session creation and agent execution ---
import asyncio

async def main():
  runner = InMemoryRunner(app_name="ParallelizationApp", agent=root_agent)
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
            parts=[types.Part(text="start the research process")],
        ),

  )
  for result in result_gen:
    print(result)

if __name__ == "__main__":
  asyncio.run(main())
