import os
import asyncio
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, Runnable
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"))

# Define the chains

summarize_chain = Runnable = (
    ChatPromptTemplate.from_messages(
        [
            ("system", "Summarize the following topic concisely"),
            ("user", "{topic}"),
        ]
    )) | llm | StrOutputParser()

question_chain = Runnable = (
    ChatPromptTemplate.from_messages(
        [
            ("system", "Generate three interesting questions about the following topic"),
            ("user", "{topic}"),
        ]
    )) | llm | StrOutputParser()

terms_chain = Runnable = (
    ChatPromptTemplate.from_messages(
        [
            ("system", "Identify 5-10 key terms from the following topic, separated by commas:"),
            ("user", "{topic}"),
        ]
    )) | llm | StrOutputParser()

# Build the parallel chain

map_chain = RunnableParallel(
    {
        "summary": summarize_chain,
        "questions": question_chain,
        "key_terms": terms_chain,
        "topic": RunnablePassthrough(),
    }
)

# Define the final synthesis prompt which will combine the parallel results.
synthesis_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """Based on the following information:
         Summary: {summary}
         Related Questions: {questions}
         Key Terms: {key_terms}
         Synthesize a comprehensive answer. """),
        ("user", "Original topic: {topic}"),
    ])

# Construct full chain
full_parallel_chain = map_chain | synthesis_prompt | llm | StrOutputParser()

async def main(topic: str) -> None:
    result = full_parallel_chain.invoke(topic)
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main("The history of space exploration"))