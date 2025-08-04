# app.py
 
import streamlit as st
import re
from utils.pdf_parser import extract_and_clean_pdf_text
from utils.url_handler import validate_and_scrape_cert_url, extract_links_from_text
from utils.skill_extractor import match_skills
 
st.title("CertiNova – Resume & Certification Verifier")
 
uploaded_resume = st.file_uploader("Upload Resume (optional)", type=["pdf"])

cert_links = st.text_area("Paste Certificate Links (one per line)")

uploaded_certs = st.file_uploader("Upload Certificate PDFs", type=["pdf"], accept_multiple_files=True)
 
# Process resume

resume_skills = []

COMMON_SKILLS = [
    "python", "pyspark", "pl/sql", "java", "scala", "data analysis", "big data", "spark", "hadoop", "mapreduce",
    "pipelines", "hive", "impala", "oracle", "kudu", "windows", "linux", "git", "gradle", "openshift", "jenkins",
    "azure", "cloud", "sql", "machine learning", "automation"
]

if uploaded_resume:
    from utils.pdf_parser import extract_name_from_text
    resume_text = extract_and_clean_pdf_text(uploaded_resume)

    # Extract candidate name from resume
    resume_name = extract_name_from_text(resume_text)

    # Extract URLs from resume text
    resume_urls = extract_links_from_text(resume_text)
    if resume_urls:
        st.subheader("Extracted URLs from Resume")
        st.write(resume_urls)

    # Basic keyword-based skill extraction
    resume_skills = [skill for skill in COMMON_SKILLS if skill.lower() in resume_text.lower()]
    st.subheader("Extracted Resume Skills")
    st.write(resume_skills)

 
# Process certificates

cert_skills = []

if uploaded_certs:
    for cert_file in uploaded_certs:
        cert_text = extract_and_clean_pdf_text(cert_file)
        cert_name = extract_name_from_text(cert_text)
        if uploaded_resume:
            if not resume_name or not cert_name or resume_name.lower() != cert_name.lower():
                st.warning(f"The name on the certificate ({cert_name}) does not match the name on the resume ({resume_name}). Skill verification skipped for this certificate.")
                continue  # Skip skill extraction for this certificate
        cert_skills.extend([skill for skill in COMMON_SKILLS if skill.lower() in cert_text.lower()])

# Extract URLs from certificate links textarea, clean and deduplicate
cert_link_urls = extract_links_from_text(cert_links)
if cert_link_urls:
    st.subheader("Extracted Certificate URLs")
    st.write(cert_link_urls)

all_urls = set(cert_link_urls)
if uploaded_resume:
    all_urls.update(resume_urls)

# Mapping of skills to synonyms/related phrases for dynamic runtime extraction
SKILL_SYNONYMS = {
    "python": ["python"],
    "pyspark": ["pyspark"],
    "pl/sql": ["pl/sql", "pl sql", "procedural language/sql"],
    "java": ["java"],
    "scala": ["scala"],
    "data analysis": ["data analysis", "analyzing data", "data analytics", "data analyst"],
    "big data": ["big data", "large-scale data", "bigdata"],
    "spark": ["spark", "apache spark"],
    "hadoop": ["hadoop", "apache hadoop"],
    "mapreduce": ["mapreduce", "map reduce"],
    "pipelines": ["pipeline", "pipelines", "data pipeline", "etl pipeline"],
    "hive": ["hive", "apache hive"],
    "impala": ["impala", "apache impala"],
    "oracle": ["oracle", "oracle database"],
    "kudu": ["kudu", "apache kudu"],
    "windows": ["windows"],
    "linux": ["linux"],
    "git": ["git", "github", "gitlab"],
    "gradle": ["gradle"],
    "openshift": ["openshift", "red hat openshift"],
    "jenkins": ["jenkins", "jenkins pipeline"],
    "azure": ["azure", "microsoft azure", "azure cloud"],
    "cloud": ["cloud", "cloud computing", "cloud architect", "cloud platform", "aws", "azure", "gcp", "google cloud", "cloud engineer"],
    "sql": ["sql", "structured query language"],
    "machine learning": ["machine learning", "ml", "deep learning", "ai", "artificial intelligence"],
    "automation": ["automation", "automated", "automating"],
}

import tempfile
import requests

def try_fetch_pdf_and_extract_skills(pdf_url):
    try:
        st.info(f"Attempting to download and parse PDF certificate from: {pdf_url}")
        import certifi
        def safe_get(url, **kwargs):
            if "drive.google.com" in url:
                return requests.get(url, verify=False, **kwargs)
            else:
                return requests.get(url, verify=certifi.where(), **kwargs)
        response = safe_get(pdf_url, stream=True, timeout=10)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()
                cert_text = extract_and_clean_pdf_text(tmp_file.name)
            content_lower = cert_text.lower()
            matched_skills = set()
            for skill, synonyms in SKILL_SYNONYMS.items():
                for phrase in synonyms:
                    if phrase in content_lower:
                        matched_skills.add(skill)
                        break
            cert_skills.extend(matched_skills)
            st.info(f"Dynamically extracted skills from PDF {pdf_url}: {matched_skills}")
            st.success(f"Fetched and processed certificate PDF: {pdf_url}")
        else:
            st.warning(f"Could not download PDF from {pdf_url}: HTTP {response.status_code}")
    except Exception as e:
        st.warning(f"Failed to process PDF from {pdf_url}: {e}")

for url in all_urls:
    clean_url = url.strip()
    if not clean_url:
        continue
    # Handle Google Drive links
    if "drive.google.com" in clean_url:
        import re
        file_id_match = re.search(r"/d/([\w-]+)", clean_url)
        if file_id_match:
            file_id = file_id_match.group(1)
            direct_pdf_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            # Download and extract name from PDF
            import tempfile
            import requests
            from utils.pdf_parser import extract_and_clean_pdf_text, extract_name_from_text
            import certifi
            def safe_get(url, **kwargs):
                if "drive.google.com" in url:
                    return requests.get(url, verify=False, **kwargs)
                else:
                    return requests.get(url, verify=certifi.where(), **kwargs)
            response = safe_get(direct_pdf_url, stream=True, timeout=10)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file.flush()
                    cert_text = extract_and_clean_pdf_text(tmp_file.name)
                cert_name = extract_name_from_certificate_text(cert_text)
                if uploaded_resume:
                    if not resume_name or not cert_name or resume_name.lower() != cert_name.lower():
                        st.warning(f"The name on the certificate ({cert_name}) does not match the name on the resume ({resume_name}). Skill verification skipped for this certificate.")
                        continue
                content_lower = cert_text.lower()
                matched_skills = set()
                for skill, synonyms in SKILL_SYNONYMS.items():
                    for phrase in synonyms:
                        if phrase in content_lower:
                            matched_skills.add(skill)
                            break
                cert_skills.extend(matched_skills)
                st.info(f"Dynamically extracted skills from PDF {direct_pdf_url}: {matched_skills}")
                st.success(f"Fetched and processed certificate PDF: {direct_pdf_url}")
            else:
                st.warning(f"Could not download PDF from {direct_pdf_url}: HTTP {response.status_code}")
            continue
        else:
            st.warning(f"Google Drive link format not recognized: {clean_url}. Please upload the PDF directly.")
    else:
        valid, content = validate_and_scrape_cert_url(clean_url)
        if valid:
            # Try to extract name from the content (if it's a PDF, not HTML/text)
            from utils.pdf_parser import extract_name_from_certificate_text, extract_name_from_text
            cert_name = extract_name_from_certificate_text(content)
            # Treat generic badge/certification titles as missing name
            KNOWN_BADGE_TITLES = [
                'AWS Certified Solutions', 'AWS Certified', 'Microsoft Certified', 'Google Certified', 'Oracle Certified', 'Udemy Certificate', 'Coursera Certificate', 'edX Certificate', 'Certified', 'Credential', 'Badge', 'Certification', 'Certificate'
            ]
            if not cert_name or cert_name.strip() in KNOWN_BADGE_TITLES or not any(char.isalpha() for char in cert_name):
                cert_name = st.text_input(f"Could not extract name from this certificate ({clean_url}). Please enter the name as it appears on the certificate:", key=clean_url)
                if not cert_name:
                    st.warning(f"No name provided for certificate ({clean_url}). Skill verification skipped for this certificate.")
                    continue
            if uploaded_resume:
                if not resume_name or not cert_name or resume_name.lower() != cert_name.lower():
                    st.warning(f"The name on the certificate ({cert_name}) does not match the name on the resume ({resume_name}). Skill verification skipped for this certificate.")
                    continue
            content_lower = content.lower()
            matched_skills = set()
            for skill, synonyms in SKILL_SYNONYMS.items():
                for phrase in synonyms:
                    if phrase in content_lower:
                        matched_skills.add(skill)
                        break
            cert_skills.extend(matched_skills)
            st.info(f"Dynamically extracted skills from {clean_url}: {matched_skills}")
            st.success(f"Fetched and processed content from: {clean_url}")
        else:
            st.warning(f"Could not access {clean_url}: {content}")

# Show result

if resume_skills:

    matched, unmatched, extra = match_skills(resume_skills, cert_skills)

    st.subheader("Skill Verification Report")

    st.write("✅ Verified Skills:", matched)

    st.write("❌ Claimed but Not Found:", unmatched)

    st.write("📌 Extra Certified Skills:", extra)

else:

    st.subheader("Skills Found in Certifications")

    st.write(cert_skills)
