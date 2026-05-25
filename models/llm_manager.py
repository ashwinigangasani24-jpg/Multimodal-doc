import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

def get_llm():
    """
    Initializes and returns the LangChain Google GenAI Chat model.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    
    # We use gemini-1.5-pro for best performance with complex text
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_tokens=2048,
        timeout=None,
        max_retries=2,
    )
    return llm

def get_embeddings():
    """
    Initializes and returns the Google GenAI Embeddings model.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return embeddings
