import fitz  # PyMuPDF
import re

def extract_and_clean_pdf_text(pdf_file):
    """
    Extracts text content from a PDF file or file-like object using PyMuPDF and cleans it.
    Args:
        pdf_file (str or file-like): Path to the PDF file or a file-like object.
    Returns:
        str: Cleaned text content.
    """
    if hasattr(pdf_file, "read"):
        # It's a file-like object (e.g., from Streamlit uploader)
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    else:
        # It's a file path
        doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned
