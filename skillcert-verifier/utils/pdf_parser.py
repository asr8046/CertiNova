import fitz  # PyMuPDF
import re
import base64
from io import BytesIO

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

def extract_all_images_from_pdf(pdf_file):
    """
    Extract all embedded images from a PDF as base64-encoded strings.
    Args:
        pdf_file (str or file-like): Path to the PDF file or a file-like object.
    Returns:
        List[str]: List of base64-encoded image strings.
    """
    images_b64 = []
    if hasattr(pdf_file, "read"):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    else:
        doc = fitz.open(pdf_file)
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            buffered = BytesIO(image_bytes)
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            images_b64.append(img_base64)
    return images_b64


def extract_faces_from_pdf_first_page(pdf_file):
    """
    Render the first page of a PDF, detect faces using OpenCV, and return cropped face images as base64 strings.
    If no face is found, return the whole page image as fallback.
    Args:
        pdf_file (str or file-like): Path to the PDF file or a file-like object.
    Returns:
        List[str]: List of base64-encoded cropped face images (or 1 full page image if none found).
    """
    import cv2
    from PIL import Image
    import numpy as np
    # Load OpenCV's pre-trained Haar Cascade for face detection
    haar_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(haar_cascade_path)

    if hasattr(pdf_file, "read"):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    else:
        doc = fitz.open(pdf_file)
    page = doc[0]
    pix = page.get_pixmap(dpi=200)
    img_bytes = pix.tobytes("png")
    pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")
    img_np = np.array(pil_img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    faces_b64 = []
    for (x, y, w, h) in faces:
        face_img = pil_img.crop((x, y, x + w, y + h))
        buffered = BytesIO()
        face_img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        faces_b64.append(img_base64)
    if not faces_b64:
        # No face found, return the full page image as fallback
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return [img_base64]
    return faces_b64

def extract_profile_image_from_pdf(pdf_file):
    """
    Extract the first embedded image from a PDF resume as a base64-encoded string.
    If no embedded image is found, return None.
    Args:
        pdf_file (str or file-like): Path to the PDF file or a file-like object.
    Returns:
        str or None: Base64-encoded image string, or None if not found.
    """
    images = extract_all_images_from_pdf(pdf_file)
    return images[0] if images else None
