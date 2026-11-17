"""Hugging Face Space / local web app: python app.py (needs gradio)."""
from pathlib import Path

import gradio as gr

from cv_ats_check import ExtractionError, analyse_file
from cv_ats_check.core import FAIL, OK
from cv_ats_check.report import MESSAGES, check_message

ICON = {OK: "✅", FAIL: "❌"}
LINK = {
    "fr": "Analyse détaillée et gratuite par IA, avec conseils par e-mail : "
          "[jobspeeder.online/analyse-cv](https://jobspeeder.online/analyse-cv?utm_source=huggingface&utm_medium=space"
          "&utm_campaign=cv-ats-check) — JobSpeeder, un assistant en recherche d'emploi.",
    "en": "Free, detailed AI analysis with tips by email: "
          "[jobspeeder.online/analyse-cv](https://jobspeeder.online/analyse-cv?utm_source=huggingface&utm_medium=space"
          "&utm_campaign=cv-ats-check) — JobSpeeder, a job search assistant.",
}


def run(file, offer, lang):
    lang = "en" if lang == "English" else "fr"
    if not file:
        return "Choisissez un CV (PDF, DOCX ou TXT)." if lang == "fr" else "Choose a CV (PDF, DOCX or TXT)."
    path = file if isinstance(file, str) else file.name
    try:
        r = analyse_file(path, offer=offer or None)
    except ExtractionError as exc:
        return f"⚠️ {exc}"
    m = MESSAGES[lang]
    out = [f"## {m['score'].format(score=r.score)}"]
    if r.keyword_score is not None:
        out.append(f"- {m['structure'].format(s=r.structure_score)}\n- {m['keywords'].format(k=r.keyword_score)}")
    out.append("")
    out += [f"{ICON.get(c.status, '⚠️')} {check_message(c, lang)}  " for c in r.checks]
    if r.keyword_score is not None:
        for key, words in (("found", r.keywords_found), ("missing", r.keywords_missing)):
            if words:
                out.append(f"\n**{m[key].split('{list}')[0].strip()}** {', '.join(words)}")
        if r.keywords_missing:
            out.append(f"\n_{m['hint_missing']}_")
    out.append("\n---\n" + LINK[lang])
    return "\n".join(out)


with gr.Blocks(title="CV ATS check — vérifier si un CV passe les ATS") as demo:
    gr.Markdown(
        "# CV ATS check\n"
        "Vérifiez si votre CV est lisible par les logiciels de recrutement (ATS) : texte, rubriques, coordonnées, dates, "
        "et mots-clés de l'offre. Analyse locale, sans IA, rien n'est conservé. Code source : "
        "[github.com/maelon111/cv-ats-check](https://github.com/maelon111/cv-ats-check).\n\n"
        "_Check whether your CV is readable by applicant tracking systems. Nothing is stored._"
    )
    with gr.Row():
        with gr.Column():
            cv = gr.File(label="CV (PDF, DOCX, TXT)", file_types=[".pdf", ".docx", ".txt"], type="filepath")
            offer = gr.Textbox(label="Offre d'emploi (facultatif) / Job offer (optional)", lines=8,
                               placeholder="Collez le texte de l'offre pour comparer les mots-clés…")
            lang = gr.Radio(["Français", "English"], value="Français", label="Langue / Language")
            go = gr.Button("Analyser / Check", variant="primary")
        with gr.Column():
            result = gr.Markdown()
    go.click(run, [cv, offer, lang], result)
    examples = Path(__file__).parent / "exemples"
    if examples.exists():
        gr.Examples([[str(examples / "cv-exemple.txt"), (examples / "offre-exemple.txt").read_text(encoding="utf-8"),
                      "Français"]], [cv, offer, lang])

if __name__ == "__main__":
    demo.launch()
