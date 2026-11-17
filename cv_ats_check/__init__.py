"""cv-ats-check: is your CV readable by an applicant tracking system (ATS)?"""
from pathlib import Path

from .core import Report, analyse, offer_keywords
from .extract import ExtractionError, read
from .report import render

__version__ = "1.0.0"
__all__ = ["analyse", "analyse_file", "offer_keywords", "render", "read", "Report", "ExtractionError"]


def analyse_file(path, offer: str | None = None) -> Report:
    """Reads a PDF, DOCX or TXT CV and returns its report."""
    doc = read(path)
    return analyse(doc.text, pages=doc.pages, file_format=doc.format, file_name=Path(path).name, offer=offer)
