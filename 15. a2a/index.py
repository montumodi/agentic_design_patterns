"""
Agent-to-Agent (A2A) Protocol Client Example

This demonstrates using the official A2A protocol to discover and communicate
with a remote agent using standardized methods.

Official A2A Protocol: https://a2a-protocol.org/
"""

import asyncio
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.client.helpers import create_text_message_object
from a2a.types import Role


async def main():
    """
    Demonstrates A2A client discovering and communicating with a weather agent.
    """
    
    print("\n" + "="*70)
    print("A2A (Agent2Agent) Protocol - Client Example")
    print("="*70)
    
    # Step 1: Discover the agent by fetching its Agent Card
    agent_url = "http://localhost:8000"
    
    print(f"\n📡 Discovering agent at: {agent_url}")
    print("   Fetching Agent Card from /.well-known/agent-card...")
    
    async with httpx.AsyncClient() as http_client:
        try:
            # Use A2ACardResolver to fetch the agent card
            resolver = A2ACardResolver(
                httpx_client=http_client,
                base_url=agent_url
            )
            agent_card = await resolver.get_agent_card()
            
            print(f"\n✓ Agent discovered: {agent_card.name}")
            print(f"  Description: {agent_card.description}")
            if agent_card.skills:
                skill_names = [skill.name for skill in agent_card.skills]
                print(f"  Skills: {', '.join(skill_names)}")
            print(f"  Protocol: {agent_card.preferred_transport}")
            
            config = ClientConfig(httpx_client=http_client)
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            
            # Step 3: Send a message using the A2A protocol
            print("\n" + "-"*70)
            print("📨 Sending message to agent...")
            print("-"*70)
            
            # Create a message using A2A helper
            message = create_text_message_object(
                role=Role.user,
                content="What's the weather like in Ealing, London?"
            )
            
            print(f"\nUser: {message.parts[0].root.text}")
            print(f"Message ID: {message.message_id}")
            
            # Send message and process responses
            # The A2A protocol handles the JSON-RPC communication
            print("\n⏳ Waiting for response...")
            
            async for event in client.send_message(message):
                # Handle different event types
                if hasattr(event, 'parts'):  # It's a Message
                    response_message = event
                    print(f"\n✓ Agent: {response_message.parts[0].root.text}")
                    break
                else:  # It's a (Task, Update) tuple
                    task, update = event
                    if update:
                        print(f"  Status: {task.status.state}")
            
            # Step 4: Send another message to demonstrate conversation
            print("\n" + "-"*70)
            print("📨 Sending follow-up message...")
            print("-"*70)
            
            followup_message = create_text_message_object(
                role=Role.user,
                content="How about New York?"
            )
            
            print(f"\nUser: {followup_message.parts[0].root.text}")
            
            async for event in client.send_message(followup_message):
                if hasattr(event, 'parts'):
                    response_message = event
                    print(f"\n✓ Agent: {response_message.parts[0].root.text}")
                    break
                    
        except httpx.ConnectError:
            print("\n❌ Error: Could not connect to agent server")
            print("   Make sure the weather agent server is running:")
            print("   python weather_agent_server.py")
            return
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return
    
    print("\n" + "="*70)
    print("✓ A2A Communication Completed Successfully")
    print("="*70)
    print("\n📚 Key A2A Concepts Demonstrated:")
    print("  • Agent Discovery via Agent Card")
    print("  • JSON-RPC 2.0 message protocol")
    print("  • Standardized message/send method")
    print("  • Task state management")
    print("  • Cross-framework compatibility")
    print("\n🔗 Learn more: https://a2a-protocol.org/")
    print()


if __name__ == "__main__":
    asyncio.run(main())
