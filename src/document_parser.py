from pathlib import Path
from docx import Document

def docx_to_text(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def save_extracted_text(source_path: Path, target_dir: Path, prefix: str) -> Path:
    text = docx_to_text(source_path)
    safe_name = source_path.stem.replace(" ", "_").lower()
    target_path = target_dir / f"{prefix}_{safe_name}.md"
    target_path.write_text(text, encoding="utf-8")
    return target_path