import fitz  # PyMuPDF
import re

def extract_name_from_text(text):
    """
    Extract a likely candidate name from general PDF text (resume, etc).
    Uses several heuristics: pattern matching, line analysis, and fallback to plausible lines.
    """
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
    Robustly extract candidate name from certificate PDF text.
    Handles Azure, AWS, Google, and generic certificate formats. Falls back to extract_name_from_text if needed.
    """
    match = re.search(r'([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+) has', text)
    if match:
        return match.group(1).strip()
    match = re.search(r'(?:This is to certify that|This certifies that) ([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)', text)
    if match:
        return match.group(1).strip()
    match = re.search(r'(?:awarded to|is awarded to) ([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)', text)
    if match:
        return match.group(1).strip()
    lines = text.splitlines()
    for line in lines:
        match = re.match(r'([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+( [A-Z][a-zA-Z]+)?)', line.strip())
        if match:
            return match.group(1).strip()
    match = re.search(r'Name[:\s]+([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)', text)
    if match:
        return match.group(1).strip()
    return extract_name_from_text(text)

def extract_and_clean_pdf_text(pdf_file):
    """
    Extract text content from a PDF file or file-like object using PyMuPDF and return cleaned text.
    Args:
        pdf_file (str or file-like): Path to the PDF file or a file-like object.
    Returns:
        str: Cleaned text content.
    """
    if hasattr(pdf_file, "read"):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    else:
        doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned
