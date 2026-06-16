import pandas as pd
from src.db import get_conn

def add_application(data: dict):
    conn = get_conn()
    conn.execute("""
        insert into applications (
            company, job_title, location, skills, jd_text,
            jd_posted_date, applied_date,
            cv_original_path, cv_text_path,
            cover_letter_original_path, cover_letter_text_path,
            status, reply_received, interview_stage, notes
        )
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        data["company"],
        data["job_title"],
        data["location"],
        data["skills"],
        data["jd_text"],
        data["jd_posted_date"],
        data["applied_date"],
        data["cv_original_path"],
        data["cv_text_path"],
        data["cover_letter_original_path"],
        data["cover_letter_text_path"],
        data["status"],
        data["reply_received"],
        data["interview_stage"],
        data["notes"],
    ])

def get_all_applications() -> pd.DataFrame:
    conn = get_conn()
    return conn.sql("""
        select
            id,
            company,
            job_title,
            location,
            skills,
            jd_posted_date,
            applied_date,
            date_diff('day', applied_date, current_date) as days_waiting,
            status,
            reply_received,
            interview_stage,
            notes,
            cv_original_path,
            cover_letter_original_path,
            created_at
        from applications
        order by applied_date desc, created_at desc
    """).df()

def replace_tracker(df: pd.DataFrame):
    conn = get_conn()
    conn.register("updated_df", df)
    conn.execute("""
        update applications
        set
            status = updated_df.status,
            reply_received = updated_df.reply_received,
            interview_stage = updated_df.interview_stage,
            notes = updated_df.notes,
            updated_at = current_timestamp
        from updated_df
        where applications.id = updated_df.id
    """)