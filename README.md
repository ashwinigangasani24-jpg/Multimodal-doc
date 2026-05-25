# Multimodal Document Analyzer

A complete web application built with Python and Streamlit to analyze, summarize, and query various document types (PDF, DOCX, PNG, JPG).

## Features
- Upload PDF, DOCX, PNG, JPG files (Multi-file support)
- Extract text, tables, and images from documents
- OCR support for scanned PDFs/images using Tesseract OCR
- Summarize document content using LangChain and Google Gemini
- Question-answering chatbot over your documents using FAISS vector search
- Detect document type (Invoice, Resume, Research paper, Bank statement, Medical report)
- Extract key information (names, dates, totals, emails, phone numbers)

## Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR (Required for image text extraction)**
   - **Windows:** Download the installer from [UB-Mannheim's Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki). Run it and install. The default installation path is usually `C:\Program Files\Tesseract-OCR\tesseract.exe`.
   - If the app still raises `TesseractNotFoundError`, set the exact executable path in your environment:
     ```powershell
     setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
     ```
   - Alternatively, add Tesseract to your PATH or update `utils/document_parser.py` to point to the installed executable.
   - **Linux/Ubuntu:** `sudo apt-get install tesseract-ocr`
   - **macOS:** `brew install tesseract`

## Local Setup

1. **Clone the repository (or extract the zip):**
   ```bash
   cd "Multimodal doc"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Add your Google Gemini API Key (`GOOGLE_API_KEY`) to the `.env` file. You can get a key from [Google AI Studio](https://aistudio.google.com/).

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Deployment Instructions

### Streamlit Cloud (Recommended for easy sharing)
1. Push your code to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
3. Click "New app", select your repository, branch, and specify `app.py` as the main file.
4. In the "Advanced settings", add your `GOOGLE_API_KEY` to the Secrets section.
5. Note: Tesseract is pre-installed on Streamlit Cloud's default Debian environment via `apt-get`, but you must add a `packages.txt` file containing `tesseract-ocr` for it to work. We have included `packages.txt` in this codebase.

### Docker Deployment
1. Build the Docker image:
   ```bash
   docker build -t multimodal-doc-analyzer .
   ```
2. Run the Docker container:
   ```bash
   docker run -p 8501:8501 --env GOOGLE_API_KEY=your_key_here multimodal-doc-analyzer
   ```
   Navigate to `http://localhost:8501` to use the app.
"# Multimodal-doc" 
