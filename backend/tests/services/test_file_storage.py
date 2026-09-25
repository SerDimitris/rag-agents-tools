from pathlib import Path

import pytest

from app.core.config import settings
from app.services.file_storage import resolve_upload_path


@pytest.fixture
def upload_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "uploads"
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(root))
    return root


def test_resolve_upload_path_inside_upload_dir(upload_root: Path) -> None:
    resolved = resolve_upload_path("uploads/customer/file.txt")
    assert resolved == (upload_root / "customer" / "file.txt").resolve()


@pytest.mark.usefixtures("upload_root")
def test_resolve_upload_path_rejects_parent_traversal() -> None:
    with pytest.raises(ValueError):
        resolve_upload_path("uploads/../secret.txt")


def test_resolve_upload_path_rejects_sibling_with_same_prefix(
    upload_root: Path,
) -> None:
    # "../uploads-evil" shares the "uploads" string prefix but is outside it.
    with pytest.raises(ValueError):
        resolve_upload_path(f"../{upload_root.name}-evil/file.txt")
