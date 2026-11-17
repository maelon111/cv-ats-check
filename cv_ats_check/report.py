"""Human-readable report, in French or English."""
from __future__ import annotations

from .core import FAIL, OK, WARN, Report

ICONS = {OK: "✔", WARN: "!", FAIL: "✘"}

MESSAGES = {
    "fr": {
        "title": "Analyse ATS du CV",
        "score": "Score global : {score}/100",
        "structure": "Lisibilité et structure : {s}/100",
        "keywords": "Mots-clés de l'offre présents : {k}/100",
        "text_readable": {OK: "Le texte est lisible par un logiciel ({words} mots).",
                          FAIL: "Presque aucun texte lisible ({words} mots) : CV scanné ou exporté en image. Un ATS ne "
                                "lit rien. Exportez-le depuis Word, Google Docs ou LibreOffice (« Enregistrer en PDF »)."},
        "characters": {OK: "Pas de caractères illisibles.",
                       WARN: "Quelques caractères illisibles ({ratio:.1%}) : icônes ou police exotique.",
                       FAIL: "Beaucoup de caractères illisibles ({ratio:.1%}) : police d'icônes ou encodage cassé ; "
                             "utilisez une police standard (Arial, Calibri, Garamond…)."},
        "layout": {OK: "Le texte se lit dans l'ordre.",
                   WARN: "Mots collés ({examples}) : la mise en page en colonnes ou en tableau est mal lue. "
                         "Préférez une seule colonne."},
        "email": {OK: "Adresse e-mail trouvée : {value}", FAIL: "Aucune adresse e-mail lisible."},
        "phone": {OK: "Téléphone trouvé : {value}", WARN: "Aucun numéro de téléphone lisible (indicatif +32, +33… conseillé)."},
        "linkedin": {OK: "Profil LinkedIn trouvé.", WARN: "Pas de lien LinkedIn (facultatif, mais apprécié)."},
        "section_experience": {OK: "Rubrique « Expérience » trouvée.",
                               FAIL: "Pas de rubrique « Expérience professionnelle » reconnaissable."},
        "section_education": {OK: "Rubrique « Formation » trouvée.", FAIL: "Pas de rubrique « Formation » reconnaissable."},
        "section_skills": {OK: "Rubrique « Compétences » trouvée.", FAIL: "Pas de rubrique « Compétences » reconnaissable."},
        "section_languages": {OK: "Rubrique « Langues » trouvée.", WARN: "Pas de rubrique « Langues »."},
        "dates": {OK: "Dates lisibles ({ranges} périodes, {years} années).",
                  WARN: "Peu de dates ({years} années) : notez « 2021 – 2024 » pour chaque poste.",
                  FAIL: "Aucune date trouvée : l'ATS ne peut pas calculer votre expérience."},
        "length": {OK: "Longueur correcte ({words} mots).",
                   WARN: "CV {too_fr} ({words} mots) : visez 300 à 900 mots."},
        "pages": {OK: "{pages} page(s).", WARN: "{pages} pages : deux pages maximum, sauf CV académique."},
        "format": {OK: "Format {format} accepté par tous les ATS.", WARN: "Format {format} : envoyez un PDF ou un DOCX."},
        "file_name": {OK: "Nom de fichier clair : {name}",
                      WARN: "Nom de fichier peu parlant ({name}) : préférez « Prenom-Nom-CV.pdf »."},
        "found": "Mots-clés de l'offre présents dans le CV : {list}",
        "missing": "Mots-clés de l'offre absents du CV : {list}",
        "hint_missing": "Ajoutez ceux qui correspondent vraiment à votre expérience, avec les mêmes mots que l'offre.",
    },
    "en": {
        "title": "CV ATS check",
        "score": "Overall score: {score}/100",
        "structure": "Readability and structure: {s}/100",
        "keywords": "Job offer keywords present: {k}/100",
        "text_readable": {OK: "Text is machine-readable ({words} words).",
                          FAIL: "Almost no readable text ({words} words): scanned or image-only CV. An ATS reads "
                                "nothing. Export it from Word, Google Docs or LibreOffice (\"Save as PDF\")."},
        "characters": {OK: "No garbled characters.",
                       WARN: "Some garbled characters ({ratio:.1%}): icons or an unusual font.",
                       FAIL: "Many garbled characters ({ratio:.1%}): icon font or broken encoding; use a standard "
                             "font (Arial, Calibri, Garamond...)."},
        "layout": {OK: "Text reads in the right order.",
                   WARN: "Glued words ({examples}): columns or tables are read in the wrong order. Use one column."},
        "email": {OK: "Email address found: {value}", FAIL: "No readable email address."},
        "phone": {OK: "Phone number found: {value}", WARN: "No readable phone number (country code recommended)."},
        "linkedin": {OK: "LinkedIn profile found.", WARN: "No LinkedIn link (optional, but appreciated)."},
        "section_experience": {OK: "\"Experience\" section found.", FAIL: "No recognisable \"Work experience\" section."},
        "section_education": {OK: "\"Education\" section found.", FAIL: "No recognisable \"Education\" section."},
        "section_skills": {OK: "\"Skills\" section found.", FAIL: "No recognisable \"Skills\" section."},
        "section_languages": {OK: "\"Languages\" section found.", WARN: "No \"Languages\" section."},
        "dates": {OK: "Readable dates ({ranges} periods, {years} years).",
                  WARN: "Few dates ({years} years): write \"2021 - 2024\" for each job.",
                  FAIL: "No dates found: the ATS cannot compute your experience."},
        "length": {OK: "Good length ({words} words).", WARN: "CV too {too_en} ({words} words): aim for 300 to 900 words."},
        "pages": {OK: "{pages} page(s).", WARN: "{pages} pages: two pages maximum, except academic CVs."},
        "format": {OK: "{format} format accepted by every ATS.", WARN: "{format} format: send a PDF or DOCX."},
        "file_name": {OK: "Clear file name: {name}", WARN: "Vague file name ({name}): prefer \"Firstname-Lastname-CV.pdf\"."},
        "found": "Job offer keywords found in the CV: {list}",
        "missing": "Job offer keywords missing from the CV: {list}",
        "hint_missing": "Add the ones that truly match your experience, using the same words as the offer.",
    },
}


def check_message(check, lang: str = "fr") -> str:
    m = MESSAGES[lang]
    template = m[check.id][check.status]
    d = dict(check.detail)
    if "examples" in d:
        d["examples"] = ", ".join(d["examples"])
    if "too" in d:
        d["too_fr"] = "trop court" if d["too"] == "short" else "trop long"
        d["too_en"] = d["too"]
    if "format" in d:
        d["format"] = d["format"].upper()
    return template.format(**d)


def render(report: Report, lang: str = "fr") -> str:
    m = MESSAGES[lang]
    lines = [m["title"], "=" * len(m["title"]), m["score"].format(score=report.score)]
    if report.keyword_score is not None:
        lines.append("  " + m["structure"].format(s=report.structure_score))
        lines.append("  " + m["keywords"].format(k=report.keyword_score))
    lines.append("")
    for c in report.checks:
        lines.append(f"[{ICONS[c.status]}] {check_message(c, lang)}")
    if report.keyword_score is not None:
        lines.append("")
        if report.keywords_found:
            lines.append(m["found"].format(list=", ".join(report.keywords_found)))
        if report.keywords_missing:
            lines.append(m["missing"].format(list=", ".join(report.keywords_missing)))
            lines.append(m["hint_missing"])
    return "\n".join(lines)
