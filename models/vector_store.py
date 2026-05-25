import os
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.llm_manager import get_embeddings, get_llm
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate

VECTOR_STORE_PATH = "vectorstore/faiss_index"

def build_vector_store(text):
    """
    Builds and saves a FAISS vector store from the given text.
    """
    embeddings = get_embeddings()
    if not embeddings:
        return False, "Embeddings not configured. Please set GOOGLE_API_KEY."
        
    try:
        # Split text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        if not chunks:
            return False, "No text to index."
            
        # Create FAISS vector store
        vector_store = FAISS.from_texts(chunks, embedding=embeddings)
        
        # Save to local disk
        vector_store.save_local(VECTOR_STORE_PATH)
        return True, "Vector store built successfully."
        
    except Exception as e:
        print(f"Error building vector store: {e}")
        return False, str(e)

def answer_question(question):
    """
    Answers a question based on the document text stored in FAISS.
    """
    embeddings = get_embeddings()
    llm = get_llm()
    
    if not embeddings or not llm:
        return "LLM or Embeddings not configured. Please set GOOGLE_API_KEY."
        
    try:
        # Load the existing FAISS index
        if not os.path.exists(VECTOR_STORE_PATH):
            return "Vector store not found. Please process a document first."
            
        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH, 
            embeddings,
            allow_dangerous_deserialization=True # Required for local FAISS loading in newer versions
        )
        
        # Set up retrieval chain
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        
        prompt_template = """
        Use the following pieces of retrieved context to answer the question. 
        If you don't know the answer, just say that you don't know. 
        Use three sentences maximum and keep the answer concise.
        
        Context: {context}
        
        Question: {input}
        
        Answer:
        """
        prompt = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "input"]
        )
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        response = retrieval_chain.invoke({"input": question})
        return response["answer"]
        
    except Exception as e:
        print(f"Error answering question: {e}")
        return f"Error: {str(e)}"
