import fitz  # PyMuPDF
import re

def extract_name_from_text(text):
    """
    Extracts a likely candidate name from general PDF text (resume, etc).
    """
    # Try to extract name from pattern 'Xxx Xxx has ...' anywhere in the text
    match = re.search(r'([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+) has', text)
    if match:
        return match.group(1).strip()
    lines = text.splitlines()
    if lines:
        first_line = lines[0].strip()
        match = re.match(r"([A-Z][a-zA-Z]* [A-Z][a-zA-Z]*)( [A-Z][a-zA-Z]*)?", first_line)
        if match:
            return match.group(0).strip()
    possible_name = None
    for line in lines[:20]:
        line = line.strip()
        if not line or len(line) < 2:
            continue
        if any(h in line.lower() for h in ['curriculum', 'resume', 'vitae', 'certificat', 'profile', 'summary', 'skills', 'objective']):
            continue
        if '@' in line or re.search(r'\d{3,}', line):
            continue
        if any(word in line.lower() for word in ['engineer', 'developer', 'data', 'project', 'manager', 'analyst', 'certified', 'certificate', 'certification', 'pl/sql', 'java', 'scala', 'cloud', 'azure', 'aws', 'gcp', 'machine learning', 'sql', 'hadoop', 'spark', 'big data', 'skills', 'experience', 'education']):
            continue
        if line.replace(' ', '').isalpha() and len(line.split()) <= 4:
            return line
        if not possible_name:
            possible_name = line
    return possible_name

def extract_name_from_certificate_text(text):
    """
    Robustly extract candidate name from certificate PDF text (handles Azure, AWS, Google, generic).
    """
    # Azure/Microsoft: 'Xxx Xxx has successfully passed' or 'Xxx Xxx has'
    match = re.search(r'([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+) has', text)
    if match:
        return match.group(1).strip()
    # AWS: 'This is to certify that Xxx Xxx has' or 'This certifies that Xxx Xxx'
    match = re.search(r'(?:This is to certify that|This certifies that) ([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)', text)
    if match:
        return match.group(1).strip()
    # Google: 'This certificate is awarded to Xxx Xxx' or 'awarded to Xxx Xxx'
    match = re.search(r'(?:awarded to|is awarded to) ([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)', text)
    if match:
        return match.group(1).strip()
    # Generic: first two or three capitalized words in any line
    lines = text.splitlines()
    for line in lines:
        match = re.match(r'([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+( [A-Z][a-zA-Z]+)?)', line.strip())
        if match:
            return match.group(1).strip()
    # Fallback: look for 'Name: Xxx Xxx' or similar patterns
    match = re.search(r'Name[:\s]+([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)', text)
    if match:
        return match.group(1).strip()
    # Fallback: use extract_name_from_text
    return extract_name_from_text(text)

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
