import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
llm_pro = ChatGoogleGenerativeAI(model="gemini-2.5-pro", api_key=os.getenv("GEMINI_API_KEY"))

# For internet search, bind google_search tool using the bind method
llm_internet_search = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    api_key=os.getenv("GEMINI_API_KEY")
).bind(tools=[{"google_search": {}}])


def classify_prompt(prompt:str) -> dict:
    system_message = {
    "role": "system",
    "content": (
    "You are a classifier that analyzes user prompts and returns one of three categories ONLY:\n\n"
    "- simple\n"
    "- reasoning\n"
    "- internet_search\n\n"
    "Rules:\n"
    "- Use 'simple' for direct factual questions that need no reasoning or current events.\n"
    "- Use 'reasoning' for logic, math, or multi-step inference questions.\n"
    "- Use 'internet_search' if the prompt refers to current events, recent data, or things not in your training data.\n\n"
    "Respond ONLY with JSON like (without any other extra information like wrapping in ```json etc):\n"
    '{ "classification": "simple" }'
    ),
    }

    user_message = {"role": "user", "content": prompt}

    reply = llm_flash.invoke([system_message, user_message])
    print(reply.content)
    return json.loads(reply.content)

def generate_response(prompt: str, classification: str) -> str:
    """Generate a response using the appropriate LLM based on classification type."""
    
    # Select the appropriate LLM based on classification
    if classification == "simple":
        llm = llm_flash
        print(f"Using Flash model for simple query")
    elif classification == "reasoning":
        llm = llm_pro
        print(f"Using Pro model for reasoning query")
    elif classification == "internet_search":
        llm = llm_internet_search
        print(f"Using Flash model with Google Search for internet search query")
    else:
        # Default to flash for unknown classifications
        llm = llm_flash
        print(f"Unknown classification, defaulting to Flash model")
    
    # Generate the response
    reply = llm.invoke([{"role": "user", "content": prompt}])
    return reply.content

# Example usage
prompt = "Explain the impact of quantum computing on cryptography."
classification_result = classify_prompt(prompt)
classification = classification_result["classification"]
print(f"\nClassification: {classification}")

response = generate_response(prompt, classification)
print(f"\nResponse: {response}")