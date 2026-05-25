import streamlit as st
import os
import json
import tempfile
from fpdf import FPDF
from dotenv import load_dotenv

from utils.document_parser import process_document
from utils.information_extractor import extract_information, summarize_document
from models.vector_store import build_vector_store, answer_question

# Load environment variables
load_dotenv()

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Multimodal Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialization & Session State ---
if "processed" not in st.session_state:
    st.session_state.processed = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "extracted_info" not in st.session_state:
    st.session_state.extracted_info = {}
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "all_tables" not in st.session_state:
    st.session_state.all_tables = []
if "all_images" not in st.session_state:
    st.session_state.all_images = []

# --- Custom Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: var(--background-color);
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)


def generate_pdf_report(summary, extracted_info):
    """Generates a PDF report of the analysis."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Document Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    # Document Type
    pdf.set_font("Arial", 'B', 12)
    doc_type = extracted_info.get("document_type", "Unknown")
    pdf.cell(0, 10, f"Detected Document Type: {doc_type}", ln=True)
    pdf.ln(5)
    
    # Extracted Info
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Extracted Key Information:", ln=True)
    pdf.set_font("Arial", '', 11)
    
    for key, val in extracted_info.items():
        if key != "document_type" and key != "error":
            if isinstance(val, list) and val:
                pdf.cell(0, 8, f"{key.capitalize()}: {', '.join(str(v) for v in val)}", ln=True)
            elif val and not isinstance(val, list):
                pdf.cell(0, 8, f"{key.capitalize()}: {val}", ln=True)
    pdf.ln(10)
    
    # Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Document Summary:", ln=True)
    pdf.set_font("Arial", '', 11)
    # Handle multi-line summary text safely
    clean_summary = summary.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_summary)
    
    # Save to temp file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name


# --- UI Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233010.png", width=80)
    st.title("DocuAnalyzer AI")
    st.markdown("Upload your documents to extract text, tables, images, and chat with the content.")
    
    api_key_input = st.text_input("Google Gemini API Key (Optional if in .env)", type="password")
    if api_key_input:
        os.environ["GOOGLE_API_KEY"] = api_key_input
        
    uploaded_files = st.file_uploader(
        "Upload Documents", 
        type=["pdf", "docx", "png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )
    
    process_btn = st.button("Process Documents", use_container_width=True, type="primary")

    if st.session_state.processed:
        st.markdown("---")
        st.subheader("Key Information")
        info = st.session_state.extracted_info
        
        doc_type = info.get("document_type", "Unknown")
        st.markdown(f"**Type:** <span style='color:green;'>{doc_type}</span>", unsafe_allow_html=True)
        
        st.markdown("**Names:**")
        st.caption(", ".join(info.get("names", [])) if info.get("names") else "None")
        
        st.markdown("**Dates:**")
        st.caption(", ".join(info.get("dates", [])) if info.get("dates") else "None")
        
        st.markdown("**Totals/Amounts:**")
        st.caption(", ".join(info.get("totals", [])) if info.get("totals") else "None")
        
        st.markdown("**Emails:**")
        st.caption(", ".join(info.get("emails", [])) if info.get("emails") else "None")
        
        st.markdown("**Phone Numbers:**")
        st.caption(", ".join(info.get("phone_numbers", [])) if info.get("phone_numbers") else "None")

        # Download Report
        if st.session_state.summary:
            st.markdown("---")
            report_path = generate_pdf_report(st.session_state.summary, st.session_state.extracted_info)
            with open(report_path, "rb") as f:
                st.download_button(
                    label="Download PDF Report",
                    data=f,
                    file_name="analysis_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# --- Main Application Logic ---
st.markdown('<div class="main-header">Multimodal Document Analyzer</div>', unsafe_allow_html=True)

if process_btn:
    if not uploaded_files:
        st.warning("Please upload at least one document.")
    elif not os.environ.get("GOOGLE_API_KEY"):
        st.error("Please provide a Google Gemini API Key.")
    else:
        with st.spinner("Analyzing documents... This may take a minute."):
            # Ensure upload dir exists
            os.makedirs("uploads", exist_ok=True)
            os.makedirs("vectorstore", exist_ok=True)
            
            combined_text = ""
            all_tables = []
            all_images = []
            
            progress_bar = st.progress(0)
            
            # 1. Parse all files
            for i, file in enumerate(uploaded_files):
                file_path = os.path.join("uploads", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                    
                parsed_data = process_document(file_path, file.name)
                combined_text += f"\n--- Content from {file.name} ---\n" + parsed_data["text"]
                all_tables.extend(parsed_data["tables"])
                all_images.extend(parsed_data["images"])
                
                progress_bar.progress(int(((i+1)/len(uploaded_files)) * 30))
            
            # Store extracted non-text modalities
            st.session_state.all_tables = all_tables
            st.session_state.all_images = all_images
            
            # 2. Extract Information (LLM)
            progress_bar.progress(50, text="Extracting key information...")
            extracted_info = extract_information(combined_text)
            st.session_state.extracted_info = extracted_info
            
            # 3. Summarize (LLM)
            progress_bar.progress(70, text="Generating summary...")
            summary = summarize_document(combined_text)
            st.session_state.summary = summary
            
            # 4. Build Vector Store (RAG)
            progress_bar.progress(90, text="Building search index...")
            success, msg = build_vector_store(combined_text)
            
            if not success:
                st.error(f"Failed to build search index: {msg}")
            
            progress_bar.progress(100, text="Done!")
            st.session_state.processed = True
            st.session_state.chat_history = [] # Reset chat
            st.rerun()

# --- Tabs for Content ---
if st.session_state.processed:
    tab1, tab2, tab3 = st.tabs(["Chat & Summary", "Extracted Tables", "Extracted Images"])
    
    with tab1:
        st.markdown('<div class="sub-header">Document Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">{st.session_state.summary}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div class="sub-header">Q&A Chatbot</div>', unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = answer_question(prompt)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
    with tab2:
        st.markdown('<div class="sub-header">Extracted Tables</div>', unsafe_allow_html=True)
        if st.session_state.all_tables:
            for i, table_df in enumerate(st.session_state.all_tables):
                st.write(f"**Table {i+1}**")
                st.dataframe(table_df, use_container_width=True)
        else:
            st.info("No tables were extracted from the uploaded documents.")
            
    with tab3:
        st.markdown('<div class="sub-header">Extracted Images</div>', unsafe_allow_html=True)
        if st.session_state.all_images:
            cols = st.columns(3)
            for i, img_bytes in enumerate(st.session_state.all_images):
                with cols[i % 3]:
                    st.image(img_bytes, caption=f"Extracted Image {i+1}", use_container_width=True)
        else:
            st.info("No images were extracted from the uploaded documents.")
else:
    st.info("Please upload documents and click 'Process Documents' to begin analysis.")
