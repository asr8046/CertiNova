# Placeholder for skill extraction logic
def match_skills(resume_skills, cert_skills):
    # Accepts lists of skills, normalizes to lowercase, and compares.
    resume_skills_set = set([s.lower() for s in resume_skills])
    cert_skills_set = set([s.lower() for s in cert_skills])
    matched = resume_skills_set & cert_skills_set
    unmatched = resume_skills_set - cert_skills_set
    extra = cert_skills_set - resume_skills_set
    return matched, unmatched, extra
