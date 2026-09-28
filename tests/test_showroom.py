import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "showroom/content/modules/ROOT/pages"


class ShowroomTests(unittest.TestCase):
    def test_lab_is_separate_and_follows_seven_state_journey(self):
        expected = ["01-observe.adoc", "02-preflight.adoc", "03-propose.adoc", "04-approve.adoc", "05-execute.adoc", "06-validate.adoc", "07-learn-reclaim.adoc"]
        self.assertTrue(all((PAGES / name).exists() for name in expected))
        joined = "\n".join((PAGES / name).read_text() for name in expected)
        for term in ("ALLOW_REVIEW", "REFUSE", "ABSTAIN", "HUMAN_APPROVAL_REQUIRED", "zero residue", "REHEARSAL"):
            self.assertIn(term, joined)

    def test_supplemental_roadshow_was_not_copied(self):
        files = [path for path in (ROOT / "showroom").rglob("*") if path.is_file()]
        self.assertLess(len(files), 20)
        self.assertFalse(any("2026_spring" in path.as_posix() for path in files))


if __name__ == "__main__":
    unittest.main()
