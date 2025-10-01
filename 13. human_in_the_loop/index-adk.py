from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
import uuid
from google.adk.runners import InMemoryRunner

from google.genai import types
from typing import Optional
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Placeholder for tools (replace with actual implementations if needed)
def troubleshoot_issue(issue: str) -> dict:
    return {"status": "success", "report": f"Troubleshooting steps for {issue}."}

def create_ticket(issue_type: str, details: str) -> dict:
    return {"status": "success", "ticket_id": "TICKET123"}

def escalate_to_human(issue_type: str) -> dict:
    # This would typically transfer to a human queue in a real system
    return {"status": "success", "message": f"Escalated {issue_type} to a human specialist."}

technical_support_agent = Agent(
    name="technical_support_specialist",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a technical support specialist for our electronics company.
    FIRST, check if the user has a support history in
    state["customer_info"]["support_history"]. If they do, reference this
    history in your responses.
    For technical issues:
    1. Use the troubleshoot_issue tool to analyze the problem.
    2. Guide the user through basic troubleshooting steps.
    3. If the issue persists, use create_ticket to log the issue.
    5
    For complex issues beyond basic troubleshooting:
    1. Use escalate_to_human to transfer to a human specialist.
    Maintain a professional but empathetic tone. Acknowledge the
    frustration technical issues can cause, while providing clear steps
    toward resolution.
    """,
    tools=[troubleshoot_issue, create_ticket, escalate_to_human]
)

def personalization_callback( callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmRequest]:
    """Adds personalization information to the LLM request."""
    # Get customer info from state
    customer_info = callback_context.state.get("customer_info")
    if customer_info:
        customer_name = customer_info.get("name", "valued customer")
        customer_tier = customer_info.get("tier", "standard")
        recent_purchases = customer_info.get("recent_purchases", [])
        personalization_note = (
        f"\nIMPORTANT PERSONALIZATION:\n"
        f"Customer Name: {customer_name}\n"
        f"Customer Tier: {customer_tier}\n"
        )
    if recent_purchases:
        personalization_note += f"Recent Purchases: {', '.join(recent_purchases)}\n"
    if llm_request.contents:
    # Add as a system message before the first content
        system_content = types.Content(
        role="system",
        parts=[types.Part(text=personalization_note)]
        )
        llm_request.contents.insert(0, system_content)

    return None # Return None to continue with the modified request

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
    runner = InMemoryRunner(technical_support_agent)
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