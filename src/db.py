import duckdb
from src.config import DB_PATH

def get_conn():
    conn = duckdb.connect(str(DB_PATH))
    conn.execute("""
        create table if not exists applications (
            id uuid default uuid(),
            company varchar,
            job_title varchar,
            location varchar,
            skills varchar,
            jd_text text,
            jd_posted_date date,
            applied_date date,
            cv_original_path varchar,
            cv_text_path varchar,
            cover_letter_original_path varchar,
            cover_letter_text_path varchar,
            status varchar default 'Applied',
            reply_received boolean default false,
            interview_stage varchar default 'Not started',
            notes text,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp
        )
    """)
    return conn