# Agent-to-Agent (A2A) Communication Pattern

![Architecture](Architecture.jpg)

## Overview

This example demonstrates the official [A2A (Agent2Agent) Protocol](https://a2a-protocol.org/), an open standard initiated by Google and donated to the Linux Foundation. The A2A protocol enables seamless communication and collaboration between AI agents built on different frameworks or by different vendors.

## What is A2A?

A2A is a standardized protocol that allows agents to:
- **Discover Capabilities**: Find other agents and their skills via Agent Cards
- **Communicate**: Exchange messages using JSON-RPC 2.0 over HTTP(S)
- **Collaborate**: Delegate tasks and share context between autonomous agents
- **Operate Independently**: Work across different frameworks (LangGraph, CrewAI, ADK, etc.)

## Key Features

- **Standardized Discovery**: Agent Cards (like business cards) describe capabilities
- **Task Management**: Create, track, and manage long-running tasks
- **Streaming Support**: Real-time updates via Server-Sent Events (SSE)
- **Enterprise Ready**: Built-in auth, security, and monitoring support
- **Framework Agnostic**: Works with any AI agent framework

## Implementation

This example shows a minimal A2A setup with:

1. **Weather Agent Server**: An A2A-compliant agent powered by an LLM (Google Gemini) that provides weather information
2. **Client**: Discovers the weather agent and sends requests using the A2A protocol
3. **Standard Protocol**: Uses official A2A SDK for Python
4. **LLM Integration**: Demonstrates how A2A agents can leverage LLMs for intelligent responses

## Use Cases

- **Multi-Framework Collaboration**: Agents built with different frameworks working together
- **Distributed AI Systems**: Specialized agents across different services/vendors
- **Agent Marketplaces**: Discovering and consuming agent services
- **Enterprise AI**: Standardized agent communication across organization
- **Microservices for AI**: Each agent as an independent, discoverable service

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirement.txt
```

### 2. Set up environment variables
Create a `.env` file with your Google Gemini API key:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Run the Weather Agent Server
```bash
python weather_agent_server.py
```

### 4. In another terminal, run the client
```bash
python index.py
```

## Project Structure

- `weather_agent_server.py` - A2A-compliant weather agent server
- `weather_agent.py` - LLM-powered weather agent using Google Gemini
- `weather_agent_executor.py` - A2A executor that handles the agent execution
- `index.py` - Client that discovers and communicates with the weather agent
- `requirement.txt` - A2A SDK, LangChain, and dependencies

## Key Concepts Demonstrated

### 1. Agent Card
Every A2A agent publishes an Agent Card at `/.well-known/agent-card` describing:
- Agent name, description, and capabilities
- Supported skills
- Service endpoint URL
- Authentication requirements

### 2. Message Exchange
Standard JSON-RPC 2.0 protocol for:
- `message/send` - Send a message and get response
- `message/stream` - Stream real-time updates
- `tasks/get` - Query task status
- `tasks/cancel` - Cancel running tasks

### 3. Task Lifecycle
Tasks progress through states:
- `submitted` → `working` → `completed`
- Or: `input-required`, `cancelled`, `failed`

## Official Resources

- **Documentation**: https://a2a-protocol.org/
- **Protocol Spec**: https://a2a-protocol.org/latest/specification/
- **Python SDK**: https://github.com/a2aproject/a2a-python
- **Samples**: https://github.com/a2aproject/a2a-samples
- **Community**: https://github.com/a2aproject/A2A/discussions

## Differences from Custom Multi-Agent Systems

| Aspect | A2A Protocol | Custom Implementation |
|--------|--------------|----------------------|
| Standard | Industry standard | Proprietary |
| Discovery | Agent Cards (standardized) | Custom discovery |
| Protocol | JSON-RPC 2.0 / gRPC | Varies |
| Interop | Cross-framework | Framework-specific |
| Tools | Official SDKs | Build from scratch |
