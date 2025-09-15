import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", api_key=os.getenv("GEMINI_API_KEY"))

# Prompt 1 - Extract Information
prompt_extract = ChatPromptTemplate.from_template(
    "Extract the technical specifications from the following text: \n\n{text_input}"
)

# Prompt 2 - Transform to JSON
prompt_transform = ChatPromptTemplate.from_template(
    "Transform the following specifications into a JSON object with 'cpu', 'memory', and 'storage' as keys: \n\n{specifications}"
)

# Build the chain
extraction_chain = prompt_extract | llm | StrOutputParser()

# Full chain
full_chain = (
    {"specifications": extraction_chain}
    | prompt_transform
    | llm
    | StrOutputParser()
)

# Run the chain
input_text = "The server has 4 cores, 16 GB RAM, and 1 TB storage."
output = full_chain.invoke({"text_input": input_text})

print("\nOutput:")
print(output)   