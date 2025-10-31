"""
Weather Agent Executor - Implements the A2A AgentExecutor interface
"""

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from weather_agent import WeatherAgent


class WeatherAgentExecutor(AgentExecutor):
    """Weather Agent Executor following A2A pattern"""
    
    def __init__(self):
        self.agent = WeatherAgent()
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the weather agent request"""
        # Get the user's input
        query = context.get_user_input()
        
        print(f"\n📨 Received query: {query}")
        
        # Get weather information
        result = await self.agent.get_weather(query)
        
        print(f"📤 Sending response: {result}")
        
        # Send the response as a message
        await event_queue.enqueue_event(new_agent_text_message(result))
    
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Cancel operation - not supported for this simple agent"""
        raise Exception('cancel not supported')
