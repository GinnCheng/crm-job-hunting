import re

COMMON_SKILLS = [
    "python", "sql", "excel", "tableau", "power bi", "aws", "azure",
    "gcp", "pandas", "numpy", "machine learning", "data analysis",
    "data visualization", "etl", "airflow", "spark", "snowflake",
    "communication", "stakeholder management"
]

def parse_jd(jd_text: str) -> dict:
    text = jd_text.strip()
    lower = text.lower()

    skills = [s for s in COMMON_SKILLS if s in lower]

    title = ""
    for line in text.splitlines()[:12]:
        if any(word in line.lower() for word in ["analyst", "engineer", "developer", "consultant", "manager"]):
            title = line.strip()
            break

    location = ""
    match = re.search(r"(Sydney|Melbourne|Brisbane|Canberra|Perth|Adelaide|Remote|Hybrid)", text, re.I)
    if match:
        location = match.group(0)

    return {
        "company": "",
        "job_title": title,
        "location": location,
        "skills": ", ".join(skills),
    }