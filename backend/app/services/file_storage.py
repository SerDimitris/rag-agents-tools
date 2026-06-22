from pathlib import Path

from app.core.config import settings


def get_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def resolve_upload_path(file_path: str) -> Path:
    upload_dir = get_upload_dir().resolve()
    resolved = (upload_dir / file_path.removeprefix("uploads/")).resolve()
    if not str(resolved).startswith(str(upload_dir)):
        raise ValueError("Invalid file path")
    return resolved


def delete_stored_file(file_path: str) -> None:
    try:
        path = resolve_upload_path(file_path)
    except ValueError:
        return
    if path.is_file():
        path.unlink()
