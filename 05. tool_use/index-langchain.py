from asyncio import tasks
import os
import asyncio
import nest_asyncio
from typing import List
from dotenv import load_dotenv
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool as langchain_tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY"))

@langchain_tool
def search_information(query: str) -> str:
    """
Provides factual information on a given topic. Use this tool to
find answers to phrases
like 'capital of France' or 'weather in London?'.
"""
    print("search_information tool called", query)

    simulated_results = {
        "weather in london?": "The weather in London is currently cloudy with a temperature of 15°C.",
        "capital of france": "The capital of France is Paris.",
        "population of earth": "The estimated population of Earth is around 8 billion people.",
        "tallest mountain": "Mount Everest is the tallest mountain above sea level.",
        "default": f"Simulated search result for '{query}': No specific information found, but the topic seems interesting."
    }
    return simulated_results.get(query.lower(), simulated_results["default"])   

tools = [search_information]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, agent_prompt)

agent_executor = AgentExecutor(agent=agent, verbose=False, tools=tools)

async def run_agent_with_tool(query: str):
    response = await agent_executor.ainvoke({"input": query})
    print(response["output"])

async def main():
    tasks = [
        run_agent_with_tool("What is the capital of France?"),
        run_agent_with_tool("What's the weather like in London?"),
        run_agent_with_tool("Tell me something about dogs.") 
        ]
    await asyncio.gather(*tasks)
nest_asyncio.apply()
asyncio.run(main())