"""Text extraction from a CV file (PDF, DOCX, TXT), the way a basic ATS parser sees it."""
from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    text: str
    pages: int | None  # None when the format has no pages (DOCX, TXT)
    format: str
    file_name: str


class ExtractionError(Exception):
    pass


def from_pdf(path: Path) -> Document:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ExtractionError("pypdf is required to read PDF files: pip install pypdf") from exc
    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # corrupted or encrypted file
        raise ExtractionError(f"unreadable PDF: {exc}") from exc
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise ExtractionError("password-protected PDF: an ATS cannot open it") from exc
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return Document("\n".join(parts), len(reader.pages), "pdf", path.name)


def from_docx(path: Path) -> Document:
    """Reads word/document.xml without any dependency (paragraphs and table cells)."""
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
    except (zipfile.BadZipFile, KeyError) as exc:
        raise ExtractionError(f"unreadable DOCX: {exc}") from exc
    xml = re.sub(r"<w:tab/>", "\t", xml)
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'")):
        text = text.replace(a, b)
    return Document(text, None, "docx", path.name)


def from_txt(path: Path) -> Document:
    raw = path.read_bytes()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return Document(raw.decode(enc), None, "txt", path.name)
        except UnicodeDecodeError:
            continue
    raise ExtractionError("unknown text encoding")  # pragma: no cover


def read(path: str | Path) -> Document:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return from_pdf(path)
    if suffix == ".docx":
        return from_docx(path)
    if suffix in (".txt", ".md"):
        return from_txt(path)
    if suffix == ".doc":
        raise ExtractionError("old .doc format: save it as PDF or DOCX, many ATS reject .doc")
    raise ExtractionError(f"unsupported format {suffix!r}: use PDF, DOCX or TXT")
