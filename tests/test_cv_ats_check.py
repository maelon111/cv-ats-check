import json
import tempfile
import unittest
from pathlib import Path

from cv_ats_check import analyse, analyse_file, offer_keywords, render
from cv_ats_check.__main__ import main
from cv_ats_check.core import find_sections

EX = Path(__file__).resolve().parent.parent / "exemples"
CV = (EX / "cv-exemple.txt").read_text(encoding="utf-8")
OFFER = (EX / "offre-exemple.txt").read_text(encoding="utf-8")


def status(report, check_id):
    return next(c.status for c in report.checks if c.id == check_id)


class TestAnalyse(unittest.TestCase):
    def test_good_cv(self):
        r = analyse(CV, file_format="pdf", file_name="Sarah-Martin-CV.pdf", pages=1)
        self.assertGreaterEqual(r.structure_score, 90)
        for c in ("email", "phone", "linkedin", "section_experience", "section_education", "section_skills", "dates"):
            self.assertEqual(status(r, c), "ok", c)

    def test_image_only_cv_scores_zero(self):
        r = analyse("   \n  ", file_format="pdf", pages=1)
        self.assertEqual(r.score, 0)
        self.assertEqual(r.checks[0].status, "fail")

    def test_missing_contact_and_sections(self):
        r = analyse("Je suis motivé et dynamique. " * 30)
        self.assertEqual(status(r, "email"), "fail")
        self.assertEqual(status(r, "section_experience"), "fail")
        self.assertEqual(status(r, "dates"), "fail")

    def test_garbled_characters(self):
        r = analyse(CV + "" * 40)
        self.assertNotEqual(status(r, "characters"), "ok")

    def test_glued_words(self):
        r = analyse(CV + "\nComptabilitégénéraleExcelWinbooks ExpérienceprofessionnelleFiduciaire "
                         "FormationbachelierHauteécole")
        self.assertEqual(status(r, "layout"), "warn")

    def test_file_name(self):
        self.assertEqual(status(analyse(CV, file_name="cv(3).pdf"), "file_name"), "warn")
        self.assertEqual(status(analyse(CV, file_name="Sarah-Martin-CV.pdf"), "file_name"), "ok")

    def test_sections_other_languages(self):
        text = "Berufserfahrung\nx\nAusbildung\ny\nKenntnisse\nz\nWerkervaring\nTalen"
        self.assertTrue({"experience", "education", "skills", "languages"} <= set(find_sections(text)))


class TestKeywords(unittest.TestCase):
    def test_offer_keywords_skip_boilerplate(self):
        kw = offer_keywords(OFFER)
        for noise in ("h/f", "cdi", "profil", "missions", "deux"):
            self.assertNotIn(noise, kw)
        self.assertIn("winbooks", kw)

    def test_feminine_and_plural_match(self):
        r = analyse(CV, offer=OFFER)
        self.assertIn("assistant comptable", r.keywords_found)
        self.assertIn("bob", r.keywords_missing)
        self.assertIsNotNone(r.keyword_score)
        self.assertEqual(r.score, round(0.6 * r.structure_score + 0.4 * r.keyword_score))


class TestCli(unittest.TestCase):
    def test_render_and_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "Sarah-Martin-CV.txt"
            p.write_text(CV, encoding="utf-8")
            r = analyse_file(p, offer=OFFER)
            self.assertIn("Score global", render(r, "fr"))
            self.assertIn("Overall score", render(r, "en"))
            json.dumps(r.to_dict())
            self.assertEqual(main([str(p), "--json"]), 0)
            self.assertEqual(main([str(p), "--min-score", "101"]), 1)
            self.assertEqual(main([str(Path(d) / "absent.pdf")]), 2)


if __name__ == "__main__":
    unittest.main()
