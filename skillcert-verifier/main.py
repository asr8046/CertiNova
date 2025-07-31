# app.py
 
import streamlit as st

from utils.pdf_parser import extract_and_clean_pdf_text
from utils.url_handler import validate_and_scrape_cert_url
from utils.skill_extractor import match_skills
 
st.title("SkillCert – Resume & Certification Verifier")
 
uploaded_resume = st.file_uploader("Upload Resume (optional)", type=["pdf"])

cert_links = st.text_area("Paste Certificate Links (one per line)")

uploaded_certs = st.file_uploader("Upload Certificate PDFs", type=["pdf"], accept_multiple_files=True)
 
# Process resume

resume_skills = []

if uploaded_resume:

    resume_text = extract_and_clean_pdf_text(uploaded_resume)

    st.subheader("Extracted Resume Text (Debug)")
    st.write(resume_text)

    # Basic keyword-based skill extraction
    COMMON_SKILLS = [
        "python", "pyspark", "pl/sql", "java", "scala", "data analysis", "big data", "spark", "hadoop", "mapreduce",
        "pipelines", "hive", "impala", "oracle", "kudu", "windows", "linux", "git", "gradle", "openshift", "jenkins",
        "azure", "cloud", "sql", "machine learning", "automation"
    ]
    resume_skills = [skill for skill in COMMON_SKILLS if skill.lower() in resume_text.lower()]
    st.subheader("Extracted Resume Skills")
    st.write(resume_skills)

 
# Process certificates

cert_skills = []

if uploaded_certs:
    for cert_file in uploaded_certs:
        cert_text = extract_and_clean_pdf_text(cert_file)
        cert_skills.extend([skill for skill in COMMON_SKILLS if skill.lower() in cert_text.lower()])

for url in cert_links.strip().splitlines():
    valid, content = validate_and_scrape_cert_url(url)
    if valid:
        cert_skills.extend([skill for skill in COMMON_SKILLS if skill.lower() in content.lower()])
    else:
        st.warning(f"Could not access {url}: {content}")

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
