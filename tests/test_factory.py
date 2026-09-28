import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class FactoryRedTests(unittest.TestCase):
    def test_required_implementation_assets_exist(self):
        required = [
            "workload/app.py", "workload/vm_client.py", "workload/Containerfile",
            "contracts/governance-policy.json", "contracts/openapi.yaml",
            "charts/virtualization-ai-301/Chart.yaml",
            "charts/virtualization-ai-301/templates/vm.yaml",
            "charts/virtualization-ai-301/templates/networkpolicy.yaml",
            "charts/virtualization-ai-301/templates/servicemonitor.yaml",
            "showroom/content/modules/ROOT/pages/01-prerequisites.adoc",
            "showroom/content/modules/ROOT/pages/05-refuse.adoc",
            "handoff/launchpad-handoff.yaml", ".github/workflows/release-images.yml",
        ]
        missing = [name for name in required if not (ROOT / name).exists()]
        self.assertEqual(missing, [], f"CDD RED: implementation assets not authored: {missing}")

    def test_presentation_has_exactly_seven_scenes_and_no_benchmark_fields(self):
        config = (ROOT / "src/demo.config.ts").read_text()
        self.assertEqual(config.count("type:"), 7)
        for forbidden in ("latency", "throughput", "performance", "faster"):
            self.assertNotIn(forbidden, config.lower())
        for required in ("ALLOW_REVIEW", "REFUSE", "ABSTAIN", "HUMAN_REVIEW_REQUIRED", "REHEARSAL"):
            self.assertIn(required, config)

    def test_blueprint_retains_unknowns_and_exclusions(self):
        blueprint = yaml.safe_load((ROOT / "demo-blueprint.yaml").read_text())
        statuses = {item["status"] for item in blueprint["source"]["observations"]}
        self.assertTrue({"verified", "unknown", "excluded"}.issubset(statuses))
        self.assertEqual(blueprint["ai_assessment"]["final_decision_owner"], "Named human reviewer")

    def test_handoff_is_noncertifying(self):
        handoff = yaml.safe_load((ROOT / "handoff/launchpad-handoff.yaml").read_text())
        self.assertEqual(handoff["status"], "PROPOSED_NOT_CERTIFIED")
        self.assertTrue(all(value is False for value in handoff["authority"].values()))

    def test_fixture_source_states_are_not_live(self):
        for path in sorted((ROOT / "public/fixtures").glob("*.json")):
            data = json.loads(path.read_text())
            self.assertNotEqual(data.get("sourceState") or data.get("source_state"), "LIVE")


if __name__ == "__main__":
    unittest.main()
