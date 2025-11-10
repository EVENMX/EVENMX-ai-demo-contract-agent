from __future__ import annotations

import io
from pathlib import Path
from typing import Callable

import pdfplumber
from docx import Document


class UnsupportedFileTypeError(ValueError):
    pass


class EmptyDocumentError(ValueError):
    pass


def extract_text(file_path: Path, original_filename: str | None = None) -> str:
    suffix = (original_filename or file_path.name).lower()
    if suffix.endswith(".pdf"):
        text = _extract_from_pdf(file_path)
    elif suffix.endswith(".docx"):
        text = _extract_from_docx(file_path)
    elif suffix.endswith(".txt"):
        text = file_path.read_text(encoding="utf-8")
    else:
        raise UnsupportedFileTypeError("Only PDF, DOCX, and TXT files are supported in the demo.")

    cleaned = text.strip()
    if not cleaned:
        raise EmptyDocumentError("Could not extract text from the provided contract.")
    return cleaned


def _extract_from_pdf(file_path: Path) -> str:
    buffer: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            buffer.append(page.extract_text() or "")
    return "\n".join(buffer)


def _extract_from_docx(file_path: Path) -> str:
    document = Document(file_path)
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    return "\n".join(paragraphs)
