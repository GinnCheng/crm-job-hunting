# Job Hunting Tracker

A small Django app to track job applications, resume versions, cover letters, interviews, outcomes, and follow-up actions.

## 1. Setup

```bash
cd job_hunting_tracker
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set:

```bash
RESUME_FOLDER=/your/resume/folder
COVER_LETTER_FOLDER=/your/cover-letter/folder
```

## 2. Create database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 3. Run

```bash
python manage.py runserver
```

Open:

- Dashboard: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## 4. Suggested workflow

1. Add companies.
2. Add job postings and paste the JD text.
3. Add resume versions and cover letter versions.
4. Add applications linking job + resume + cover letter.
5. Add interview records as they happen.
6. Add outcome review when rejected / failed / withdrawn.

## 5. Notes

This MVP intentionally starts with Django Admin because it is the fastest way to get CRUD, search, filters, file upload, and user login.
