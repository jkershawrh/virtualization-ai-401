import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class ReleaseWorkflowTests(unittest.TestCase):
    def test_workflow_has_immutable_supply_chain_gates(self):
        text = (ROOT / ".github/workflows/release-images.yml").read_text()
        for required in (
            "expected_sha", "linux/amd64", "severity-cutoff: high", "fail-build: true",
            "spdx-json", "cosign sign", "slsaprovenance", "docker pull \"$digest_ref\"",
            "virtualization-ai-401-presentation", "virtualization-ai-401-operations-adapter",
        ):
            self.assertIn(required, text)

    def test_authored_container_bases_are_digest_pinned(self):
        for relative in ("Containerfile", "workload/Containerfile"):
            for line in (ROOT / relative).read_text().splitlines():
                if line.startswith("FROM "):
                    image = line.split()[1]
                    self.assertRegex(image, r"@sha256:[0-9a-f]{64}$")
                    self.assertNotIn(":latest", image)

    def test_handoff_contains_no_credentials_or_certification(self):
        text = (ROOT / "handoff/launchpad-handoff.yaml").read_text().lower()
        for forbidden in ("api_key:", "password:", "token:", "bearer "):
            self.assertNotIn(forbidden, text)
        handoff = yaml.safe_load(text)
        authority = handoff["factory_receipt"]["authority"]
        self.assertFalse(authority["certified"])
        self.assertFalse(authority["promotion_eligible"])


if __name__ == "__main__":
    unittest.main()
