import os
import requests
from typing import List, Dict, Any, TypedDict
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langgraph.graph import StateGraph, END

import dotenv
# Load environment variables (e.g., OPENAI_API_KEY)
dotenv.load_dotenv()

# --- 1. Data Preparation (Preprocessing) ---
# Performance Optimization: Cache downloaded file and vectorstore to avoid redundant processing
DATA_FILE = "state_of_the_union.txt"
VECTORSTORE_DIR = "faiss_vectorstore"

def load_or_download_data():
    """Load data from cache or download if not available."""
    if not Path(DATA_FILE).exists():
        print(f"Downloading data from GitHub...")
        url = "https://github.com/langchain-ai/langchain/blob/master/docs/docs/how_to/state_of_the_union.txt"
        res = requests.get(url)
        with open(DATA_FILE, "w") as f:
            f.write(res.text)
    else:
        print(f"Using cached data file: {DATA_FILE}")
    
    loader = TextLoader(f'./{DATA_FILE}')
    documents = loader.load()
    return documents

def create_or_load_vectorstore():
    """Create vectorstore from documents or load from disk if available."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=os.environ["GEMINI_API_KEY"]
    )
    
    if Path(VECTORSTORE_DIR).exists():
        print(f"Loading cached vectorstore from {VECTORSTORE_DIR}...")
        vectorstore = FAISS.load_local(
            VECTORSTORE_DIR, 
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("Creating new vectorstore...")
        documents = load_or_download_data()
        # Chunk documents
        text_splitter = CharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)
        # Embed and store chunks in FAISS
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        # Save vectorstore for future use
        vectorstore.save_local(VECTORSTORE_DIR)
        print(f"Vectorstore saved to {VECTORSTORE_DIR}")
    
    return vectorstore

# Initialize vectorstore and retriever
vectorstore = create_or_load_vectorstore()
retriever = vectorstore.as_retriever()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, google_api_key=os.environ["GEMINI_API_KEY"])

# --- 2. Define the State for LangGraph ---
class RAGGraphState(TypedDict):
    question: str
    documents: List[Document]
    generation: str

# --- 3. Define the Nodes (Functions) ---
def retrieve_documents_node(state: RAGGraphState) -> RAGGraphState:
    """Retrieves documents based on the user's question."""
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question, "generation": ""}

def generate_response_node(state: RAGGraphState) -> RAGGraphState:
    """Generates a response using the LLM based on retrieved
    documents."""
    question = state["question"]
    documents = state["documents"]
    # Prompt template from the PDF
    template = """You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know.
    Use three sentences maximum and keep the answer concise.
    Question: {question}
    Context: {context}
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)
    # Format the context from the documents
    context = "\n\n".join([doc.page_content for doc in documents])
    # Create the RAG chain
    rag_chain = prompt | llm | StrOutputParser()
    # Invoke the chain
    generation = rag_chain.invoke({"context": context, "question":
    question})
    return {"question": question, "documents": documents, "generation": generation}

# --- 4. Build the LangGraph Graph ---
workflow = StateGraph(RAGGraphState)
# Add nodes
workflow.add_node("retrieve", retrieve_documents_node)

workflow.add_node("generate", generate_response_node)
# Set the entry point
workflow.set_entry_point("retrieve")
# Add edges (transitions)
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)
# Compile the graph
app = workflow.compile()

# --- 5. Run the RAG Application ---
if __name__ == "__main__":
    print("\n--- Running RAG Query ---")
    query = "What did the president say about Justice Breyer"
    inputs = {"question": query}
    for s in app.stream(inputs):
        print(s)
    print("\n--- Running another RAG Query ---")
    query_2 = "What did the president say about the economy?"
    inputs_2 = {"question": query_2}
    for s in app.stream(inputs_2):
        print(s)