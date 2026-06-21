import streamlit as st
from datetime import date
import altair as alt
import pandas as pd

from src.config import JOB_DOC_ROOT, CV_EXTRACTED_DIR, CL_EXTRACTED_DIR
from src.jd_parser import parse_jd
from src.document_parser import save_extracted_text
from src.repository import (
    add_application,
    get_all_applications,
    get_application_details,
    replace_tracker,
    delete_application,
)

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


def render_bar_chart(data, x, y, x_title=None, y_title=None):
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(
                x,
                sort=None,
                title=x_title,
                axis=alt.Axis(labelAngle=-35),
            ),
            y=alt.Y(y, title=y_title),
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)


def build_file_link(relative_path):
    if relative_path is None or pd.isna(relative_path):
        return None

    relative_path = str(relative_path).strip()

    if not relative_path:
        return None

    file_path = JOB_DOC_ROOT / relative_path

    if not file_path.exists():
        return None

    return file_path.resolve().as_uri()


def get_selected_row_index(selection_event):
    if not selection_event:
        return None

    selection = getattr(selection_event, "selection", None)

    if selection is None and isinstance(selection_event, dict):
        selection = selection_event.get("selection")

    if selection is None:
        return None

    rows = getattr(selection, "rows", None)

    if rows is None and isinstance(selection, dict):
        rows = selection.get("rows")

    if not rows:
        return None

    return rows[0]


def render_application_materials(application_id):
    application_details = get_application_details(application_id)

    if application_details is None:
        st.warning("Selected application could not be found.")
        return

    st.caption(
        f"{application_details['company']} | "
        f"{application_details['job_title']} | "
        f"Applied {application_details['applied_date']}"
    )

    link_col1, link_col2 = st.columns(2)

    cv_link = build_file_link(application_details["cv_original_path"])
    cl_link = build_file_link(application_details["cover_letter_original_path"])

    with link_col1:
        if cv_link:
            st.markdown(f"[Open CV]({cv_link})")
            st.caption(application_details["cv_original_path"])
        else:
            st.warning("CV file not found.")

    with link_col2:
        if cl_link:
            st.markdown(f"[Open Cover Letter]({cl_link})")
            st.caption(application_details["cover_letter_original_path"])
        else:
            st.warning("Cover Letter file not found.")

    jd_text = application_details["jd_text"]
    if pd.isna(jd_text) or not str(jd_text).strip():
        jd_text = "No JD text saved for this application."

    st.text_area(
        "JD",
        value=jd_text,
        height=360,
        disabled=True,
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
        tracker_display_df = df.drop(
            columns=["cv_original_path", "cover_letter_original_path"],
            errors="ignore",
        )
        try:
            selection_event = st.dataframe(
                tracker_display_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
            )
        except TypeError:
            st.dataframe(
                tracker_display_df,
                use_container_width=True,
                hide_index=True,
            )
            selection_event = None
            st.warning(
                "Row selection needs a newer Streamlit version. "
                "Upgrade Streamlit to click rows and view materials."
            )
        selected_row_index = get_selected_row_index(selection_event)

        st.divider()
        st.subheader("Application materials")

        if selected_row_index is None:
            st.info("Select an application row to view its saved materials.")
        else:
            selected_application_id = df.iloc[selected_row_index]["id"]
            render_application_materials(selected_application_id)

        st.divider()
        st.subheader("Edit tracker fields")

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

        st.divider()

        st.subheader("Delete application")

        delete_options = df.apply(
            lambda row: (
                f"{row['company']} | "
                f"{row['job_title']} | "
                f"{row['applied_date']} | "
                f"{row['id']}"
            ),
            axis=1,
        ).tolist()

        delete_option = st.selectbox(
            "Select application to delete",
            options=delete_options,
        )

        delete_id = delete_option.split(" | ")[-1]

        if st.button("Delete selected application"):
            delete_application(delete_id)
            st.success(f"{delete_option} deleted.")
            st.rerun()


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

            week_periods = df["applied_date"].dt.to_period("W-SUN")
            week_range = pd.period_range(
                week_periods.min(),
                week_periods.max(),
                freq="W-SUN",
            )
            weekly = (
                week_periods.value_counts()
                .sort_index()
                .reindex(week_range, fill_value=0)
                .rename_axis("week")
                .reset_index(name="count")
            )
            weekly["week"] = weekly["week"].apply(
                lambda period: (
                    f"{period.start_time:%y%m%d}-"
                    f"{period.end_time:%y%m%d}"
                )
            )

            render_bar_chart(
                weekly,
                x="week",
                y="count",
                x_title="Week",
                y_title="Applications",
            )

        with col2:
            st.markdown("### Monthly applications")

            month_periods = df["applied_date"].dt.to_period("M")
            month_range = pd.period_range(
                month_periods.min(),
                month_periods.max(),
                freq="M",
            )
            monthly = (
                month_periods.value_counts()
                .sort_index()
                .reindex(month_range, fill_value=0)
                .rename_axis("month")
                .reset_index(name="count")
            )
            monthly["month"] = monthly["month"].astype(str)

            render_bar_chart(
                monthly,
                x="month",
                y="count",
                x_title="Month",
                y_title="Applications",
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

            render_bar_chart(
                status_stats,
                x="status",
                y="count",
                x_title="Status",
                y_title="Applications",
            )

        with col4:
            st.markdown("### Interview stage")

            stage_stats = (
                df["interview_stage"]
                .value_counts()
                .reset_index()
            )

            stage_stats.columns = ["stage", "count"]

            render_bar_chart(
                stage_stats,
                x="stage",
                y="count",
                x_title="Stage",
                y_title="Applications",
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

            render_bar_chart(
                location_stats,
                x="location",
                y="count",
                x_title="Location",
                y_title="Applications",
            )

        with col6:
            st.markdown("### Reply rate")

            reply_stats = (
                df["reply_received"]
                .value_counts()
                .reset_index()
            )

            reply_stats.columns = ["reply", "count"]

            render_bar_chart(
                reply_stats,
                x="reply",
                y="count",
                x_title="Reply received",
                y_title="Applications",
            )
