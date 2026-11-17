"""Command line: python -m cv_ats_check mon-cv.pdf [--offre offre.txt] [--lang en] [--json]"""
import argparse
import json
import sys
from pathlib import Path

from . import ExtractionError, analyse_file, render


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="cv-ats-check",
                                description="Vérifie si un CV est lisible par un logiciel de recrutement (ATS). "
                                            "Checks whether a CV is readable by an applicant tracking system.")
    p.add_argument("cv", help="CV au format PDF, DOCX ou TXT / CV file (PDF, DOCX, TXT)")
    p.add_argument("--offre", "--offer", dest="offer",
                   help="fichier texte de l'offre d'emploi, pour comparer les mots-clés / job offer text file")
    p.add_argument("--lang", choices=("fr", "en"), default="fr", help="langue du rapport / report language")
    p.add_argument("--json", action="store_true", help="sortie JSON / JSON output")
    p.add_argument("--min-score", type=int, default=0,
                   help="code de sortie 1 si le score est inférieur / exit code 1 below this score")
    a = p.parse_args(argv)
    offer = Path(a.offer).read_text(encoding="utf-8", errors="replace") if a.offer else None
    try:
        report = analyse_file(a.cv, offer=offer)
    except (ExtractionError, FileNotFoundError) as exc:
        print(f"cv-ats-check: {exc}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render(report, a.lang))
    return 1 if report.score < a.min_score else 0


if __name__ == "__main__":
    sys.exit(main())
