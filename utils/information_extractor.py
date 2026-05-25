import json
from langchain_core.prompts import PromptTemplate
from models.llm_manager import get_llm

def extract_information(text):
    """
    Uses the LLM to detect the document type and extract key information.
    """
    llm = get_llm()
    if not llm:
        return {"error": "LLM not configured. Please set GOOGLE_API_KEY."}

    prompt_template = """
    You are an expert document analyzer. Analyze the following document text and extract the required information.
    
    Document Text:
    {text}
    
    Required Information:
    1. Document Type: Classify the document into one of the following types: Invoice, Resume, Research paper, Bank statement, Medical report, or Other.
    2. Names: Any prominent names of people or companies mentioned.
    3. Dates: Any important dates (e.g., invoice date, DOB, publication date).
    4. Totals/Amounts: Any total amounts, balances, or key financial figures.
    5. Emails: Any email addresses found.
    6. Phone Numbers: Any phone numbers found.
    
    Output the result strictly as a valid JSON object with the following keys:
    "document_type", "names", "dates", "totals", "emails", "phone_numbers".
    For lists of items (names, dates, totals, emails, phone_numbers), output a JSON array of strings.
    If an item is not found, output an empty array.
    
    JSON Output:
    """
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain = prompt | llm
    
    try:
        # We limit the text to avoid token limits for basic extraction
        max_chars = 15000 
        truncated_text = text[:max_chars]
        
        response = chain.invoke({"text": truncated_text})
        content = response.content
        
        # Clean up the markdown formatting if the model wraps it in ```json
        content = content.replace("```json", "").replace("```", "").strip()
        
        extracted_data = json.loads(content)
        return extracted_data
    except Exception as e:
        print(f"Error extracting information: {e}")
        return {
            "document_type": "Unknown",
            "names": [],
            "dates": [],
            "totals": [],
            "emails": [],
            "phone_numbers": [],
            "error": str(e)
        }

def summarize_document(text):
    """
    Uses the LLM to generate a concise summary of the document.
    """
    llm = get_llm()
    if not llm:
        return "LLM not configured. Please set GOOGLE_API_KEY."

    prompt_template = """
    Please provide a comprehensive and concise summary of the following document.
    Highlight the main points, purpose, and key takeaways.
    
    Document Text:
    {text}
    
    Summary:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain = prompt | llm
    
    try:
        max_chars = 30000 # Allow larger context for summarization
        truncated_text = text[:max_chars]
        
        response = chain.invoke({"text": truncated_text})
        return response.content
    except Exception as e:
        print(f"Error summarizing document: {e}")
        return f"Error generating summary: {str(e)}"
