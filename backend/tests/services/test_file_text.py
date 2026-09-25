from pathlib import Path

import pytest

from app.services.file_text import (
    get_file_extension,
    is_allowed_file,
    read_text_from_file,
)


def test_get_file_extension() -> None:
    assert get_file_extension("report.PDF") == ".pdf"
    assert get_file_extension("notes.txt") == ".txt"


def test_is_allowed_file() -> None:
    assert is_allowed_file("report.pdf") is True
    assert is_allowed_file("image.png") is False


def test_read_text_from_file_txt(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("Hello banking world", encoding="utf-8")
    assert read_text_from_file(path) == "Hello banking world"


def test_read_text_from_file_unsupported(tmp_path: Path) -> None:
    path = tmp_path / "sample.png"
    path.write_bytes(b"binary")
    with pytest.raises(ValueError, match="Unsupported file type"):
        read_text_from_file(path)
