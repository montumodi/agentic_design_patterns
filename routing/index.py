import os
from httpcore import request
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

# Define simulated sub agent handlers
def booking_handler(request: str) -> str:
    """Simulates the Booking Agent handling a request."""
    print("\n--- DELEGATING TO BOOKING HANDLER ---")
    return f"Booking Handler processed request: '{request}'. Result:Simulated booking action."

def info_handler(request: str) -> str:
    """Simulates the Info Agent handling a request."""
    print("\n--- DELEGATING TO INFO HANDLER ---")
    return f"Info Handler processed request: '{request}'. Result:Simulated info action."

def unclear_handler(request: str) -> str:
    """Simulates the Unclear Agent handling a request."""
    print("\n--- DELEGATING TO UNCLEAR HANDLER ---")
    return f"Coordinator could not delegate request: '{request}'. Please clarify"

# Define coordinator router chain
# This chain decides which handler to delegate to based on the request type
coordinator_router_prompt = ChatPromptTemplate.from_messages([
    ("system", """Analyze the user's request and determine which specialized agent should process it.
    - If the request is related to booking flights or hotels, output 'booker'.
    - For all other general information questions, output 'info'.
    - If the request is unclear or doesn't fit either category, output 'unclear'.
    ONLY output one word: "booker", "info", or "unclear"."""),
    ("user", "{request}")
])

coordinator_router_chain = coordinator_router_prompt | llm | StrOutputParser()

# Define the delegation logic
# Use runnable to route based on the router chain's output.
# Define the branches for the runnable branch.

branches = {
    "booker": RunnablePassthrough.assign(output=lambda x:booking_handler(x['request']['request'])),
    "info": RunnablePassthrough.assign(output=lambda x:info_handler(x['request']['request'])),
    "unclear": RunnablePassthrough.assign(output=lambda x:unclear_handler(x['request']['request'])),
}

# Create the runnable branch. It takes the output of the router chain
# and routes the original inpput('request') to the corresponding handler.

delegation_branch = RunnableBranch(
    (lambda x: x['decision'].strip() == 'booker', branches['booker']),
    (lambda x: x['decision'].strip() == 'info', branches['info']),
    branches['unclear']
)

# Combine the router chain and the delegation branch into single runnable
# The router chain's output is passed along with the original input to the delegation branch.

coordinator_agent = {
    "decision": coordinator_router_chain,
    "request": RunnablePassthrough()
} | delegation_branch | (lambda x: x['output'])

print("--- Running with a booking request ---")
request_a = "Book me a flight to London."
result_a = coordinator_agent.invoke({"request": request_a})
print(f"Final Result A: {result_a}")

print("\n--- Running with an info request ---")
request_b = "What is the capital of Italy?"
result_b = coordinator_agent.invoke({"request": request_b})
print(f"Final Result B: {result_b}")
print("\n--- Running with an unclear request ---")
request_c = "Tell me about quantum physics."
result_c = coordinator_agent.invoke({"request": request_c})
print(f"Final Result C: {result_c}")