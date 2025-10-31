"""
Weather Agent - LLM-powered agent that provides weather information
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WeatherAgent:
    """LLM-powered weather agent"""
    
    def __init__(self):
        """Initialize the weather agent with LLM"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # Create a prompt template for weather queries
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful weather assistant agent. When asked about weather, 
provide realistic and detailed weather information for the requested city. 
Include temperature in both Fahrenheit and Celsius, conditions, and any relevant details.
Be conversational and helpful. If a city is not specified, politely ask which city they're interested in.

Note: You're providing simulated weather data for demonstration purposes."""),
            ("user", "{query}")
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    async def get_weather(self, query: str) -> str:
        """Get weather information using LLM based on query"""
        try:
            # Invoke the LLM chain
            result = await self.chain.ainvoke({"query": query})
            return result
        except Exception as e:
            return f"Sorry, I encountered an error processing your weather request: {str(e)}"
