import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PATH = PROJECT_ROOT / os.getenv("DB_PATH", "data/applications.duckdb")

JOB_DOC_ROOT = Path(
    os.getenv("JOB_DOC_ROOT", str(Path.home() / "Documents/job-hunting-files"))
)

EXTRACTED_DOC_ROOT = PROJECT_ROOT / "data" / "extracted_docs"
CV_EXTRACTED_DIR = EXTRACTED_DOC_ROOT / "cvs"
CL_EXTRACTED_DIR = EXTRACTED_DOC_ROOT / "cover_letters"

for path in [DB_PATH.parent, CV_EXTRACTED_DIR, CL_EXTRACTED_DIR]:
    path.mkdir(parents=True, exist_ok=True)