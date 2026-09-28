import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class FactoryTests(unittest.TestCase):
    def test_required_401_assets_exist(self):
        required = ["workload/app.py", "workload/vm_client.py", "workload/Containerfile", "contracts/operation-request.schema.json", "contracts/operation-response.schema.json", "charts/virtualization-ai-401/Chart.yaml", "charts/virtualization-ai-401/templates/persistentvolumeclaim.yaml", "showroom/content/modules/ROOT/pages/01-observe.adoc", "showroom/content/modules/ROOT/pages/07-learn-reclaim.adoc", "handoff/launchpad-handoff.yaml", ".github/workflows/release-images.yml"]
        self.assertEqual([name for name in required if not (ROOT / name).exists()], [])

    def test_presentation_has_exactly_seven_journey_scenes(self):
        config = (ROOT / "src/demo.config.ts").read_text()
        self.assertEqual(config.count("type:"), 7)
        for required in ("OBSERVE", "PREFLIGHT", "PROPOSE", "APPROVE", "EXECUTE", "VALIDATE", "LEARN", "ALLOW_REVIEW", "REFUSE", "ABSTAIN"):
            self.assertIn(required, config)
        for forbidden in ("latency", "throughput", "utilization", "performance", "faster"):
            self.assertNotIn(forbidden, config.lower())

    def test_blueprint_pins_prerequisite_and_preserves_authority(self):
        blueprint = yaml.safe_load((ROOT / "demo-blueprint.yaml").read_text())
        self.assertEqual(blueprint["sources"]["prerequisite"]["revision"], "91e30a4af72bb4a15a4e5dfe2f29abb5692c698f")
        self.assertFalse(blueprint["authority"]["automated_remediation"])
        self.assertFalse(blueprint["authority"]["llm_may_execute"])

    def test_handoff_is_noncertifying_and_zero_seat(self):
        handoff = yaml.safe_load((ROOT / "handoff/launchpad-handoff.yaml").read_text())
        self.assertEqual(handoff["status"], "PROPOSED_NOT_CERTIFIED")
        self.assertTrue(all(value is False for value in handoff["authority"].values()))
        self.assertEqual(handoff["catalog"]["max_seats"], 0)
        self.assertFalse(handoff["catalog"]["orderable"])

    def test_fixtures_are_honest_rehearsal(self):
        for path in sorted((ROOT / "public/fixtures").glob("*.json")):
            data = json.loads(path.read_text())
            self.assertEqual(data["source_state"], "REHEARSAL")
            self.assertFalse(data["authority"]["automated_action_performed"])


if __name__ == "__main__":
    unittest.main()
