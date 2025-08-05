# app.py
 
import streamlit as st
import re
from utils.pdf_parser import extract_and_clean_pdf_text
from utils.url_handler import validate_and_scrape_cert_url, extract_links_from_text
from utils.skill_extractor import match_skills
from utils.pdf_parser import extract_name_from_certificate_text, extract_name_from_text

st.set_page_config(page_title="CertiNova – Skill Verifier", page_icon="📑", layout="wide")

st.markdown("""
<style>
    /* Animated gradient background for the whole app */
    body {
        background: linear-gradient(-45deg, #f9f9f9, #e0e7ff, #c1f0f6, #f9e0ff);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .main {
        background: transparent !important;
    }
    .block-container {padding-top: 2rem;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/certificate.png", width=80)
    st.title("CertiNova")
    st.markdown("**Skill Verifier**")
    st.markdown(":information_source: Upload your resume and certificates or paste certificate links for instant skill verification.")
    uploaded_resume = st.file_uploader("Upload Resume (optional)", type=["pdf"])
    uploaded_certs = st.file_uploader("Upload Certificate PDFs", type=["pdf"], accept_multiple_files=True)
    cert_links = st.text_area("Paste Certificate Links (one per line)")
    st.markdown("---")
    st.caption("Made with :heart: by CertiNova Team")

st.title("📑 CertiNova – Skill Verifier")
st.markdown(
    """
    <span style='color:#4F8BF9;font-size:18px;'>Easily verify claimed skills by matching your resume with uploaded certificates and online credentials.</span>
    """,
    unsafe_allow_html=True,
)
 
# Process resume

resume_skills = []

COMMON_SKILLS = [
    "python", "pyspark", "pl/sql", "java", "scala", "data analysis", "big data", "spark", "hadoop", "mapreduce",
    "pipelines", "hive", "impala", "oracle", "kudu", "windows", "linux", "git", "gradle", "openshift", "jenkins",
    "azure", "cloud", "sql", "machine learning", "automation"
]

if uploaded_resume:
    from utils.pdf_parser import extract_name_from_text
    with st.spinner("Extracting information from resume..."):
        resume_text = extract_and_clean_pdf_text(uploaded_resume)
        resume_name = extract_name_from_text(resume_text)
        resume_urls = extract_links_from_text(resume_text)
        resume_skills = [skill for skill in COMMON_SKILLS if skill.lower() in resume_text.lower()]
    with st.expander("🔗 URLs Extracted from Resume", expanded=False):
        if resume_urls:
            st.write(resume_urls)
        else:
            st.info("No URLs found in resume.")
    with st.expander("🧑‍💼 Extracted Resume Skills", expanded=True):
        if resume_skills:
            st.success(resume_skills)
        else:
            st.warning("No skills found in resume.")

 
# Process certificates

cert_skills = []

if uploaded_certs:
    st.markdown("---")
    st.subheader("📄 Uploaded Certificates Analysis")
    if len(uploaded_certs) > 1:
        cert_cols = st.columns(len(uploaded_certs))
        for idx, cert_file in enumerate(uploaded_certs):
            with cert_cols[idx]:
                cert_text = extract_and_clean_pdf_text(cert_file)
                cert_name = extract_name_from_text(cert_text)
                st.markdown(f"**Certificate {idx+1}:**")
                st.caption(f"Name on certificate: **{cert_name}**")
                if uploaded_resume:
                    if not resume_name or not cert_name or resume_name.lower() != cert_name.lower():
                        st.warning(f"Name mismatch: {cert_name} vs {resume_name}")
                        continue
                found_skills = [skill for skill in COMMON_SKILLS if skill.lower() in cert_text.lower()]
                cert_skills.extend(found_skills)
                if found_skills:
                    st.success(f"Skills found: {found_skills}")
                else:
                    st.info("No skills found in this certificate.")
    else:
        for cert_file in uploaded_certs:
            with st.container():
                cert_text = extract_and_clean_pdf_text(cert_file)
                cert_name = extract_name_from_text(cert_text)
                st.markdown(f"**Certificate:**")
                st.caption(f"Name on certificate: **{cert_name}**")
                if uploaded_resume:
                    if not resume_name or not cert_name or resume_name.lower() != cert_name.lower():
                        st.warning(f"Name mismatch: {cert_name} vs {resume_name}")
                        continue
                found_skills = [skill for skill in COMMON_SKILLS if skill.lower() in cert_text.lower()]
                cert_skills.extend(found_skills)
                if found_skills:
                    st.success(f"Skills found: {found_skills}")
                else:
                    st.info("No skills found in this certificate.")

# Extract URLs from certificate links textarea, clean and deduplicate
cert_link_urls = extract_links_from_text(cert_links)
if cert_link_urls:
    with st.expander("🌐 Extracted Certificate URLs", expanded=False):
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
            cert_name = extract_name_from_certificate_text(content)
            # Treat generic badge/certification titles as missing name
            KNOWN_BADGE_TITLES = [
                'AWS Certified Solutions', 'AWS Certified', 'Microsoft Certified', 'Google Certified', 'Oracle Certified',
                'Udemy Certificate', 'Coursera Certificate', 'edX Certificate', 'Certified', 'Credential', 'Badge', 'Certification', 'Certificate'
            ]
            if (not cert_name or cert_name.strip() in KNOWN_BADGE_TITLES or not any(char.isalpha() for char in cert_name)):
                cert_name = st.text_input(
                    f"Could not extract name from this certificate ({clean_url}). Please enter the name as it appears on the certificate:",
                    key=clean_url
                )
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

st.markdown("---")

if resume_skills:
    matched, unmatched, extra = match_skills(resume_skills, cert_skills)
    st.subheader("📊 Skill Verification Report")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Verified Skills", len(matched))
        st.write(matched if matched else "-")
    with col2:
        st.metric("❌ Not Found", len(unmatched))
        st.write(unmatched if unmatched else "-")
    with col3:
        st.metric("📌 Extra Certified", len(extra))
        st.write(extra if extra else "-")
else:
    st.subheader("🏅 Skills Found in Certifications")
    if cert_skills:
        st.success(cert_skills)
    else:
        st.info("No skills found in certifications.")

st.markdown("---")
st.caption("© 2025 CertiNova | All rights reserved.")
