"""
A2A Weather Agent Server

A simple A2A-compliant agent that provides weather information.
Based on the official A2A helloworld example.

Official A2A Documentation: https://a2a-protocol.org/
"""

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    TransportProtocol,
)
from weather_agent_executor import WeatherAgentExecutor


def main():
    """Start the A2A Weather Agent server."""
    
    print("\n" + "="*70)
    print("A2A Weather Agent Server")
    print("="*70)
    
    # Define the agent's skill
    skill = AgentSkill(
        id='weather_info',
        name='Weather Information',
        description='Provides current weather information for various cities',
        tags=['weather', 'forecast', 'temperature'],
        examples=['What is the weather in San Francisco?', 'How about New York?'],
    )
    
    # Create the Agent Card
    agent_card = AgentCard(
        name='Weather Agent',
        description='A simple agent that provides weather information for various cities',
        url='http://localhost:8000',
        version='1.0.0',
        default_input_modes=['text/plain'],
        default_output_modes=['text/plain'],
        capabilities=AgentCapabilities(
            streaming=False,
            push_notifications=False,
        ),
        skills=[skill],
        preferred_transport=TransportProtocol.jsonrpc,
    )
    
    print(f"\n📋 Agent Card:")
    print(f"  Name: {agent_card.name}")
    print(f"  Description: {agent_card.description}")
    print(f"  Skills: {skill.name}")
    print(f"  URL: {agent_card.url}")
    print(f"  Protocol: {agent_card.preferred_transport}")
    
    # Create the request handler with agent executor
    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    # Create the A2A server application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    print(f"\n🌐 Server starting on {agent_card.url}")
    print(f"📡 Agent Card available at: {agent_card.url}/.well-known/agent-card")
    print("\n✓ Server ready to accept A2A protocol messages")
    print("  Press Ctrl+C to stop\n")
    print("-"*70)
    
    # Start the server
    uvicorn.run(server.build(), host='0.0.0.0', port=8000, log_level='warning')


if __name__ == '__main__':
    main()
