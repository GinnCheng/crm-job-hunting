import streamlit as st
from datetime import date
import pandas as pd

from src.config import JOB_DOC_ROOT, CV_EXTRACTED_DIR, CL_EXTRACTED_DIR
from src.jd_parser import parse_jd
from src.document_parser import save_extracted_text
from src.repository import add_application, get_all_applications, replace_tracker

st.set_page_config(page_title="Job Hunting CRM", layout="wide")

st.title("Job Hunting CRM")

tab_add, tab_tracker, tab_analytics = st.tabs(
    ["Add Application", "Tracker", "Analytics"]
)



def list_docx_relative(folder_name: str):
    folder = JOB_DOC_ROOT / folder_name

    if not folder.exists():
        return []

    return sorted(
        [
            str(p.relative_to(JOB_DOC_ROOT))
            for p in folder.rglob("*.docx")
        ]
    )

with tab_add:
    st.subheader("Add new application")

    jd_text = st.text_area("Paste JD", height=300)

    parsed = parse_jd(jd_text) if jd_text else {
        "company": "",
        "job_title": "",
        "location": "",
        "skills": "",
    }

    company = st.text_input("Company", value=parsed["company"])
    job_title = st.text_input("Job Title", value=parsed["job_title"])
    location = st.text_input("Location", value=parsed["location"])
    skills = st.text_area("Skills", value=parsed["skills"], height=80)

    jd_posted_date = st.date_input("JD posted date", value=date.today())
    applied_date = st.date_input("Applied date", value=date.today())

    st.divider()
    st.caption(f"Document root: {JOB_DOC_ROOT}")

    cv_files = list_docx_relative("CV")
    cl_files = list_docx_relative("CoverLetters")

    if not cv_files:
        st.warning("No CV files found under JOB_DOC_ROOT/CV")

    if not cl_files:
        st.warning("No Cover Letter files found under JOB_DOC_ROOT/CoverLetters")

    cv_relative_path = st.selectbox("Browse CV", options=cv_files)
    cl_relative_path = st.selectbox("Browse Cover Letter", options=cl_files)


    status = st.selectbox(
        "Status",
        ["Applied", "No Reply", "Rejected", "HR Interview", "Technical Interview", "Final Interview", "Offer", "Withdrawn"],
    )

    reply_received = st.checkbox("Reply received")
    interview_stage = st.selectbox(
        "Interview stage",
        ["Not started", "HR", "Technical", "Hiring Manager", "Final", "Offer", "Rejected"],
    )

    notes = st.text_area("Notes", height=100)

    if st.button("Save application", type="primary"):

        if not cv_relative_path or not cl_relative_path:
            st.error("Please select both CV and Cover Letter.")
            st.stop()

        cv_original = JOB_DOC_ROOT / cv_relative_path
        cl_original = JOB_DOC_ROOT / cl_relative_path

        cv_text_path = ""
        cl_text_path = ""

        if cv_original.exists():
            cv_text_path = save_extracted_text(cv_original, CV_EXTRACTED_DIR, company or "cv")

        if cl_original.exists():
            cl_text_path = save_extracted_text(cl_original, CL_EXTRACTED_DIR, company or "cl")

        add_application({
            "company": company,
            "job_title": job_title,
            "location": location,
            "skills": skills,
            "jd_text": jd_text,
            "jd_posted_date": jd_posted_date,
            "applied_date": applied_date,
            "cv_original_path": cv_relative_path,
            "cv_text_path": str(cv_text_path),
            "cover_letter_original_path": cl_relative_path,
            "cover_letter_text_path": str(cl_text_path),
            "status": status,
            "reply_received": reply_received,
            "interview_stage": interview_stage,
            "notes": notes,
        })

        st.success("Application saved.")

with tab_tracker:
    st.subheader("Application tracker")

    df = get_all_applications()

    if df.empty:
        st.info("No applications yet.")
    else:
        editable_columns = [
            "status",
            "reply_received",
            "interview_stage",
            "notes",
        ]

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            disabled=[col for col in df.columns if col not in editable_columns],
        )

        if st.button("Save tracker changes"):
            replace_tracker(edited_df)
            st.success("Tracker updated.")


with tab_analytics:
    st.subheader("Analytics")

    df = get_all_applications()

    if df.empty:
        st.info("No applications yet.")

    else:
        df["applied_date"] = pd.to_datetime(df["applied_date"])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Weekly applications")

            weekly = (
                df.set_index("applied_date")
                  .resample("W")
                  .size()
                  .reset_index(name="count")
            )

            st.bar_chart(
                weekly,
                x="applied_date",
                y="count"
            )

        with col2:
            st.markdown("### Monthly applications")

            monthly = (
                df.set_index("applied_date")
                  .resample("M")
                  .size()
                  .reset_index(name="count")
            )

            st.bar_chart(
                monthly,
                x="applied_date",
                y="count"
            )

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("### Status distribution")

            status_stats = (
                df["status"]
                .value_counts()
                .reset_index()
            )

            status_stats.columns = ["status", "count"]

            st.bar_chart(
                status_stats,
                x="status",
                y="count"
            )

        with col4:
            st.markdown("### Interview stage")

            stage_stats = (
                df["interview_stage"]
                .value_counts()
                .reset_index()
            )

            stage_stats.columns = ["stage", "count"]

            st.bar_chart(
                stage_stats,
                x="stage",
                y="count"
            )

        col5, col6 = st.columns(2)

        with col5:
            st.markdown("### Location distribution")

            location_stats = (
                df["location"]
                .fillna("Unknown")
                .replace("", "Unknown")
                .value_counts()
                .reset_index()
            )

            location_stats.columns = ["location", "count"]

            st.bar_chart(
                location_stats,
                x="location",
                y="count"
            )

        with col6:
            st.markdown("### Reply rate")

            reply_stats = (
                df["reply_received"]
                .value_counts()
                .reset_index()
            )

            reply_stats.columns = ["reply", "count"]

            st.bar_chart(
                reply_stats,
                x="reply",
                y="count"
            )