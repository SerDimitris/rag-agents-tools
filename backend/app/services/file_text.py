from pathlib import Path

from pypdf import PdfReader

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".csv", ".json"}


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def read_text_from_file(path: Path) -> str:
    extension = path.suffix.lower()
    if extension in {".txt", ".md", ".csv", ".json"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if extension == ".pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    raise ValueError(f"Unsupported file type: {extension}")
