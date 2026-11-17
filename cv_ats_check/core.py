"""ATS readiness checks for a CV, plus keyword coverage against a job offer.

Everything runs locally with simple, explainable rules: no AI, no network, no data sent anywhere.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass, field

from .stopwords import STOPWORDS, SHORT_TERMS

OK, WARN, FAIL = "ok", "warn", "fail"

# Section headings in French, English, Dutch, German, Spanish and Arabic (normalised: lower case, no accents)
SECTIONS = {
    "experience": ["experience", "experiences", "parcours professionnel", "emplois", "work experience", "employment",
                   "professional experience", "work history", "career history", "werkervaring", "ervaring",
                   "berufserfahrung", "berufliche erfahrung", "experiencia", "experiencia laboral", "الخبرة",
                   "الخبرات", "الخبرة المهنية"],
    "education": ["formation", "formations", "etudes", "diplomes", "education", "academic background",
                  "qualifications", "opleiding", "opleidingen", "ausbildung", "bildungsweg", "studium", "formacion",
                  "educacion", "التعليم", "المؤهلات", "التكوين"],
    "skills": ["competences", "savoir-faire", "skills", "technical skills", "key skills", "competencies",
               "vaardigheden", "competenties", "kenntnisse", "fahigkeiten", "kompetenzen", "habilidades",
               "competencias", "المهارات", "الكفاءات"],
    "languages": ["langues", "languages", "talen", "talenkennis", "sprachen", "sprachkenntnisse", "idiomas", "اللغات"],
    "summary": ["profil", "resume", "a propos", "objectif", "summary", "profile", "about me", "objective", "profiel",
                "over mij", "kurzprofil", "uber mich", "perfil", "sobre mi", "نبذة", "الملف الشخصي"],
}
REQUIRED_SECTIONS = ("experience", "education", "skills")

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RES = (re.compile(r"(?:\+|\b00)\d{1,3}[\s./-]?(?:\(0\)[\s./-]?)?\d(?:[\s./-]?\d){7,11}"),
             re.compile(r"\b0\d(?:[\s./-]?\d){7,9}\b"))
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w%-]+", re.I)
YEAR_RE = re.compile(r"\b(19[6-9]\d|20[0-4]\d)\b")
RANGE_RE = re.compile(r"\b(?:19|20)\d{2}\s*(?:-|–|—|à|to|bis|tot|/|>)\s*(?:(?:19|20)\d{2}|present|aujourd|now|current|"
                      r"heute|actuel|en cours|nu|heden|actualidad|presente)", re.I)
URL_RE = re.compile(r"(?:https?://|www\.)\S+|\S+@\S+")
BAD_FILE_RE = re.compile(r"^(?:cv|resume|curriculum(?: vitae)?|document|doc|scan|img|image|untitled|sans titre|"
                         r"nouveau document|new document)?[\s_\-.()\d]*$", re.I)


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def tokens(text: str) -> list[str]:
    # keeps c++, c#, node.js, .net, sap/4hana-like words as single tokens
    return [t.strip(".-/") or t for t in re.findall(r"[\w+#./-]*[\w+#]", normalise(text)) if t]


def stem(word: str) -> str:
    """Very light stemming, applied to both the offer and the CV: plural "s" and French feminine "e"."""
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    if len(word) > 5 and word.endswith("e"):
        word = word[:-1]
    return word


@dataclass
class Check:
    id: str
    status: str
    points: float
    max_points: float
    detail: dict = field(default_factory=dict)


@dataclass
class Report:
    score: int
    structure_score: int
    keyword_score: int | None
    checks: list[Check]
    sections_found: list[str]
    keywords_found: list[str]
    keywords_missing: list[str]
    words: int
    pages: int | None
    format: str

    def to_dict(self) -> dict:
        return asdict(self)


def find_sections(text: str) -> list[str]:
    found = []
    lines = [normalise(l).strip(" \t:•-–—|*#") for l in text.splitlines()]
    short = [l for l in lines if 0 < len(l) <= 45]
    for key, heads in SECTIONS.items():
        for l in short:
            if any(l == h or l.startswith(h + " ") or l.startswith(h + ":") or l.endswith(" " + h) for h in heads):
                found.append(key)
                break
    return found


def offer_keywords(offer: str, limit: int = 25) -> list[str]:
    toks = [t for t in tokens(offer) if (len(t) >= 3 or t in SHORT_TERMS) and t not in STOPWORDS and not t.isdigit()]
    counts = Counter(stem(t) for t in toks)
    first = {}
    for i, t in enumerate(toks):
        first.setdefault(stem(t), i)
    # frequent two-word terms ("gestion de projet" -> "gestion projet" once stop words are removed)
    bigrams = Counter(f"{stem(a)} {stem(b)}" for a, b in zip(toks, toks[1:]))
    terms = [(c, -first[w], w) for w, c in counts.items()]
    terms += [(c + 0.5, -first[b.split()[0]], b) for b, c in bigrams.items() if c >= 2]
    terms.sort(reverse=True)
    accented = {normalise(w): w for w in re.findall(r"[\w+#./-]*[\w+#]", offer.lower())}
    surface = {}
    for t in toks:  # display the word as written in the offer (accents included), not its stem
        surface.setdefault(stem(t), accented.get(t, t))
    out, seen = [], set()
    for _, _, term in terms:
        if term in seen:
            continue
        # a bigram already covers its two words
        if " " in term:
            seen.update(term.split())
        seen.add(term)
        out.append(" ".join(surface.get(w, w) for w in term.split()))
        if len(out) >= limit:
            break
    return out


def keyword_coverage(cv_text: str, offer: str) -> tuple[list[str], list[str]]:
    cv_stems = {stem(t) for t in tokens(cv_text)}
    cv_norm = " ".join(stem(t) for t in tokens(cv_text))
    found, missing = [], []
    for k in offer_keywords(offer):
        s = " ".join(stem(w) for w in normalise(k).split())
        hit = (f" {s} " in f" {cv_norm} ") if " " in s else (s in cv_stems)
        (found if hit else missing).append(k)
    return found, missing


def analyse(text: str, *, pages: int | None = None, file_format: str = "pdf", file_name: str = "",
            offer: str | None = None) -> Report:
    checks: list[Check] = []
    clean = text.strip()
    words = len(re.findall(r"\w+", clean))

    # 1. Is there any text at all? (scanned or image-only PDF = an ATS reads nothing)
    if words < 40:
        checks.append(Check("text_readable", FAIL, 0, 30, {"words": words}))
        return Report(0, 0, 0 if offer else None, checks, [], [], offer_keywords(offer) if offer else [], words, pages,
                      file_format)
    checks.append(Check("text_readable", OK, 30, 30, {"words": words}))

    # 2. Garbled characters (icon fonts, broken encodings, "(cid:12)" artefacts)
    bad = sum(1 for c in clean if c == "�" or 0xE000 <= ord(c) <= 0xF8FF or (ord(c) < 32 and c not in "\n\r\t"))
    bad += clean.count("(cid:") * 5
    ratio = bad / max(len(clean), 1)
    checks.append(Check("characters", OK if ratio < 0.003 else WARN if ratio < 0.02 else FAIL,
                        7 if ratio < 0.003 else 3 if ratio < 0.02 else 0, 7, {"ratio": round(ratio, 4)}))

    # 3. Words glued together: columns or tables read in the wrong order
    no_urls = URL_RE.sub(" ", clean)
    glued = [w for w in re.findall(r"[^\W\d_]{23,}", no_urls)]
    checks.append(Check("layout", OK if len(glued) < 3 else WARN, 4 if len(glued) < 3 else 1, 4,
                        {"examples": glued[:3]}))

    # 4. Contact details
    emails = EMAIL_RE.findall(clean)
    checks.append(Check("email", OK if emails else FAIL, 10 if emails else 0, 10, {"value": emails[0] if emails else ""}))
    phone = next((m.group(0) for r in PHONE_RES for m in r.finditer(clean)), "")
    checks.append(Check("phone", OK if phone else WARN, 7 if phone else 0, 7, {"value": phone.strip()}))
    linkedin = LINKEDIN_RE.search(clean)
    checks.append(Check("linkedin", OK if linkedin else WARN, 2 if linkedin else 0, 2,
                        {"value": linkedin.group(0) if linkedin else ""}))

    # 5. Standard section headings
    sections = find_sections(clean)
    for key, pts in (("experience", 10), ("education", 7), ("skills", 7), ("languages", 3)):
        ok = key in sections
        status = OK if ok else (FAIL if key in REQUIRED_SECTIONS else WARN)
        checks.append(Check(f"section_{key}", status, pts if ok else 0, pts))

    # 6. Dates the parser can turn into a timeline
    ranges = RANGE_RE.findall(clean)
    years = set(YEAR_RE.findall(clean))
    if ranges or len(years) >= 3:
        checks.append(Check("dates", OK, 7, 7, {"ranges": len(ranges), "years": len(years)}))
    else:
        checks.append(Check("dates", WARN if years else FAIL, 3 if years else 0, 7, {"ranges": 0, "years": len(years)}))

    # 7. Length
    if 250 <= words <= 1100:
        checks.append(Check("length", OK, 6, 6, {"words": words}))
    else:
        checks.append(Check("length", WARN, 3, 6, {"words": words, "too": "short" if words < 250 else "long"}))
    if pages is not None:
        checks.append(Check("pages", OK if pages <= 2 else WARN, 3 if pages <= 2 else 1, 3, {"pages": pages}))

    # 8. File format and name
    checks.append(Check("format", OK if file_format in ("pdf", "docx") else WARN,
                        3 if file_format in ("pdf", "docx") else 1, 3, {"format": file_format}))
    if file_name:
        stem_name = file_name.rsplit(".", 1)[0]
        good = not BAD_FILE_RE.match(stem_name) and len(re.findall(r"[^\W\d_]{2,}", stem_name)) >= 2
        checks.append(Check("file_name", OK if good else WARN, 3 if good else 0, 3, {"name": file_name}))

    earned = sum(c.points for c in checks)
    total = sum(c.max_points for c in checks)
    structure = round(100 * earned / total)

    found: list[str] = []
    missing: list[str] = []
    kw_score = None
    if offer and offer.strip():
        found, missing = keyword_coverage(clean, offer)
        n = len(found) + len(missing)
        kw_score = round(100 * len(found) / n) if n else 0
    score = structure if kw_score is None else round(0.6 * structure + 0.4 * kw_score)
    return Report(score, structure, kw_score, checks, sections, found, missing, words, pages, file_format)
