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

    def test_journey_is_executable_truthful_and_participant_safe(self):
        pages = "\n".join(path.read_text() for path in sorted(PAGES.glob("*.adoc")))
        for heading in ("Show", "Learn", "Do", "Prove"):
            self.assertIn(f"== {heading}", pages)
        self.assertGreaterEqual(pages.count('role="execute"'), 10)
        for contract in ("/healthz", "/metrics", "/api/v1/operations", "ai_participated"):
            self.assertIn(contract, pages)
        self.assertIn("PRESENTATION_URL", pages)
        self.assertNotIn("SHOWROOM_URL", pages)
        self.assertIn("VirtualMachines", pages)
        self.assertIn("PersistentVolumeClaims", pages)
        self.assertIn("Virtualization + AI 301", pages)
        self.assertIn("Virtualization + AI 501", pages)
        self.assertIn("Launchpad owns namespace reclamation", pages)
        self.assertNotIn("uninstall the candidate release", pages.lower())


if __name__ == "__main__":
    unittest.main()
